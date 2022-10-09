from pydantic import BaseModel, EmailStr, HttpUrl


class Register(BaseModel):
    username: str
    password: str
    e_mail: EmailStr
    avatar: HttpUrl | None
