from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pony.orm import commit, db_session

from core.models.user import User
from core.schemas.user import Login, Register, Token
from views import JWT_ALGORITHM, JWT_SECRET_KEY

VERIFY_TOKEN_EXPIRE_DAYS = 1.0
LOGIN_TOKEN_EXPIRE_DAYS = 7.0

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@router.post("/", response_model=Token)
async def register(schema: Register):
    with db_session:
        if User.exists(name=schema.username):
            raise HTTPException(status_code=422, detail="username was taken!")

        if User.exists(e_mail=schema.e_mail):
            raise HTTPException(status_code=422, detail="email was taken!")

        # store avatar to disk

        user = User(
            name=schema.username,
            password=password_context.hash(schema.password),
            e_mail=schema.e_mail,
            has_avatar=schema.avatar is not None,
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


@router.post("/login", response_model=Token)
def login(form_data: Login):
    with db_session:
        user = User.get(name=form_data.username)

        if not user:
            raise HTTPException(status_code=401, detail="username not found!")

        if not password_context.verify(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="passwords don't match!")

        token_data = {"sub": "login", "username": user.name}
        token = create_access_token(token_data, timedelta(days=LOGIN_TOKEN_EXPIRE_DAYS))

        return Token(token=token)
