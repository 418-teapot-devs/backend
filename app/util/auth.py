from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.util.errors import INVALID_TOKEN_EXCEPTION

JWT_SECRET_KEY = "92294169bb3637efe9a56293025e8d463089d43f8f1bd1e78c67c8e197a7ef1e"
JWT_ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("username")

        if username is None:
            raise INVALID_TOKEN_EXCEPTION

    except JWTError:
        raise INVALID_TOKEN_EXCEPTION

    return username


def get_user_and_subject(token: str):
    invalid_token_exception = HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("username")
        subject = payload.get("sub")

        if username is None or subject is None:
            raise invalid_token_exception

    except JWTError:
        raise invalid_token_exception

    return [username, subject]
