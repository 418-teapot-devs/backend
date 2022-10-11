from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from pony.orm import commit, db_session

from core.models.user import User
from core.schemas.user import Register

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/")
def register(schema: Register):
    with db_session:
        if User.exists(name=schema.username):
            raise HTTPException(status_code=422, detail="Username was taken!")

        if User.exists(e_mail=schema.e_mail):
            raise HTTPException(status_code=422, detail="E-Mail was taken!")

        # store avatar to disk

        User(
            name=schema.username,
            password=password_context.hash(schema.password),
            e_mail=schema.e_mail,
            has_avatar=schema.avatar is not None,
        )
        commit()

    return {}
