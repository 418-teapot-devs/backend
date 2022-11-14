from datetime import timedelta

from fastapi import APIRouter, Depends, Header ,HTTPException, UploadFile
from passlib.context import CryptContext
from pony.orm import commit, db_session

from app.models.user import User
from app.schemas.user import Login, LoginResponse, Register, Token, UserProfile, ChangePassWord
from app.util.assets import ASSETS_DIR, get_user_avatar
from app.util.auth import create_access_token, get_current_user

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

        # verify_token = create_access_token(
        #     {"sub": "verify", "username": user.name},
        #     timedelta(days=VERIFY_TOKEN_EXPIRE_DAYS),
        # )

        # send verify token via e-mail

        login_token = create_access_token(
            {"sub": "login", "username": user.name},
            timedelta(days=LOGIN_TOKEN_EXPIRE_DAYS),
        )

        return Token(token=login_token)


@router.post("/login", response_model=LoginResponse)
def login(form_data: Login):
    with db_session:
        user = User.get(name=form_data.username)

        if not user:
            raise HTTPException(status_code=401, detail="username not found!")

        if not password_context.verify(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="passwords don't match!")

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
            raise HTTPException(status_code=404, detail="username not found!")

    return UserProfile(
            username=user.name, email=user.email, avatar_url=get_user_avatar(user))


@router.patch("/profile/")
def get_profile(avatar: UploadFile, token: str = Header() ):
    username = get_current_user(token)

    if avatar.content_type != "image/png":
        raise HTTPException(status_code=422, detail="invalid picture format")

    with db_session:
        user = User.get(name=username)

        if not user:
            raise HTTPException(status_code=404, detail="username not found!")

        with open(f"{ASSETS_DIR}/users/{username}.png", "wb") as f:
            f.write(avatar.file.read())
            user.has_avatar = True

    return UserProfile(
            username=user.name, email=user.email, avatar_url=get_user_avatar(user))


@router.put("/password/")
def change_password(form_data: ChangePassWord, token: str = Header() ):
    username = get_current_user(token)

    with db_session:
        user = User.get(name=username)

        if not user:
            raise HTTPException(status_code=404, detail="username not found!")

        if not password_context.verify(form_data.old_password, user.password):
            raise HTTPException(status_code=401, detail="passwords don't match!")

        user.password=password_context.hash(form_data.new_password)
        commit()

