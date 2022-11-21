from fastapi import HTTPException
from password_validator import PasswordValidator
from pydantic import BaseModel, EmailStr, validator

from app.util.errors import VALUE_NOT_VALID_PASSWORD

pass_validator = (
    PasswordValidator()
    .min(8)
    .max(255)
    .has()
    .uppercase()
    .has()
    .lowercase()
    .has()
    .digits()
)


class Register(BaseModel):
    username: str
    password: str
    email: EmailStr

    @validator("password")
    def password_is_correct(cls, v):
        if not pass_validator.validate(v):
            raise VALUE_NOT_VALID_PASSWORD
        return v


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str


class UserProfile(BaseModel):
    username: str
    email: str
    avatar_url: str | None


class LoginResponse(BaseModel):
    token: str
    profile: UserProfile


class Recover(BaseModel):
    email: str


class ChangePassWord(BaseModel):
    old_password: str
    new_password: str

    @validator("new_password")
    def password_is_correct(cls, v):
        if not pass_validator.validate(v):
            raise VALUE_NOT_VALID_PASSWORD
        return v


class ResetPassword(BaseModel):
    new_password: str

    @validator("new_password")
    def password_is_correct(cls, v):
        if not pass_validator.validate(v):
            raise VALUE_NOT_VALID_PASSWORD
        return v
