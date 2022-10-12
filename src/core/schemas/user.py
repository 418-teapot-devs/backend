from fastapi import HTTPException
from password_validator import PasswordValidator
from pydantic import BaseModel, EmailStr, validator

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
    e_mail: EmailStr

    @validator("password")
    def password_is_correct(cls, v):
        if not pass_validator.validate(v):
            raise HTTPException(status_code=422, detail="value is not a valid password")

        return v


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
