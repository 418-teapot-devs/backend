import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

ASSETS_DIR = os.environ["PYROBOTS_ASSETS"]

JWT_SECRET_KEY = "92294169bb3637efe9a56293025e8d463089d43f8f1bd1e78c67c8e197a7ef1e"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: str | None = None


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=404,
        detail="Username not found",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    #    user = get_user(fake_users_db, username=token_data.username)
    #    if user is None:
    #        raise credentials_exception
    return username
