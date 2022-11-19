from datetime import timedelta
from shutil import  copyfile

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from pony.orm import commit, db_session

from app.models.user import User
from app.models.robot import Robot
from app.schemas.user import (
    ChangePassWord,
    Login,
    LoginResponse,
    Register,
    Token,
    UserProfile,
)
from app.util.assets import ASSETS_DIR, get_user_avatar
from app.util.auth import create_access_token, get_current_user, get_user_and_subject
from app.util.errors import *
from app.util.mail import send_verification_token

VERIFY_TOKEN_EXPIRE_DAYS = 1.0
LOGIN_TOKEN_EXPIRE_DAYS = 7.0

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/", response_model=Token, status_code=201)
def register(schema: Register = Depends(), avatar: UploadFile | None = None):
    if avatar and avatar.content_type != "image/png":
        raise HTTPException(status_code=422, detail="invalid picture format")

    with db_session:
        err = []
        if User.exists(name=schema.username):
            err.append("Username was taken!")

        if User.exists(email=schema.email):
            err.append("E-Mail was taken!")

        if len(err) > 0:
            raise HTTPException(status_code=409, detail=err)

        # store avatar to disk
        if avatar:
            with open(f"{ASSETS_DIR}/users/{schema.username}.png", "wb") as f:
                f.write(avatar.file.read())

        user = User(
            name=schema.username,
            password=password_context.hash(schema.password),
            email=schema.email,
            has_avatar=avatar is not None,
        )
        commit()

        verify_token = create_access_token(
            {"sub": "verify", "username": user.name},
            timedelta(days=VERIFY_TOKEN_EXPIRE_DAYS),
        )

        send_verification_token(user.email, verify_token)

        login_token = create_access_token(
            {"sub": "login", "username": user.name},
            timedelta(days=LOGIN_TOKEN_EXPIRE_DAYS),
        )


        # Create deafults robots
        default_1 = Robot(owner=user, name="default_1", has_avatar=True)
        default_2 = Robot(owner=user, name="default_2", has_avatar=True)
        commit()

        copyfile(f"{ASSETS_DIR}/defaults/avatars/default_1.png", f"{ASSETS_DIR}/robots/avatars/{default_1.id}.png")
        copyfile(f"{ASSETS_DIR}/defaults/code/default_1.py", f"{ASSETS_DIR}/robots/code/{default_1.id}.py")

        copyfile(f"{ASSETS_DIR}/defaults/avatars/default_2.png", f"{ASSETS_DIR}/robots/avatars/{default_2.id}.png")
        copyfile(f"{ASSETS_DIR}/defaults/code/default_2.py", f"{ASSETS_DIR}/robots/code/{default_2.id}.py")

        return Token(token=login_token)


@router.post("/login", response_model=LoginResponse)
def login(form_data: Login):
    with db_session:
        user = User.get(name=form_data.username)

        if not user:
            raise NON_EXISTANT_USER_OR_PASSWORD_ERROR

        if not user.is_verified:
            raise USER_NOT_VERIFIED_ERROR

        if not password_context.verify(form_data.password, user.password):
            raise NON_EXISTANT_USER_OR_PASSWORD_ERROR

        profile = UserProfile(
            username=user.name, email=user.email, avatar_url=get_user_avatar(user)
        )

    token_data = {"sub": "login", "username": form_data.username}
    token = create_access_token(token_data, timedelta(days=LOGIN_TOKEN_EXPIRE_DAYS))

    return LoginResponse(token=token, profile=profile)


@router.get("/profile/")
def get_profile(token: str = Header()):
    username = get_current_user(token)

    with db_session:
        user = User.get(name=username)

        if not user:
            raise USER_NOT_FOUND_ERROR

    return UserProfile(
        username=user.name, email=user.email, avatar_url=get_user_avatar(user)
    )


@router.patch("/profile/")
def update_profile(avatar: UploadFile, token: str = Header()):
    username = get_current_user(token)

    if avatar.content_type != "image/png":
        raise INVALID_PICTURE_FORMAT_ERROR

    with db_session:
        user = User.get(name=username)

        if not user:
            raise USER_NOT_FOUND_ERROR

        with open(f"{ASSETS_DIR}/users/{username}.png", "wb") as f:
            f.write(avatar.file.read())
            user.has_avatar = True

    return UserProfile(
        username=user.name, email=user.email, avatar_url=get_user_avatar(user)
    )


@router.put("/password/")
def change_password(form_data: ChangePassWord, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        user = User.get(name=username)

        if not user:
            raise USER_NOT_FOUND_ERROR

        if not password_context.verify(form_data.old_password, user.password):
            raise NON_EXISTANT_USER_OR_PASSWORD_ERROR

        if form_data.old_password == form_data.new_password:
            raise CURRENT_PASSWORD_EQUAL_NEW_PASSWORD

        user.password = password_context.hash(form_data.new_password)
        commit()


@router.get("/verify/", response_class=RedirectResponse)
def verify(token: str):
    username, subject = get_user_and_subject(token)

    verify_success = False
    with db_session:
        user = User.get(name=username)

        # chances for user to not exist are astronomically low
        if user and subject == "verify":
            verify_success = True
            user.is_verified = True

    return f"http://localhost:3000/login?verify_success={verify_success}"
