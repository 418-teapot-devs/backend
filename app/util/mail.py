import asyncio
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType

MAIL_USERNAME = "pyrobots.teapot@gmail.com"
MAIL_PASSWORD = "lbyqdaxqkwfhhpcp"
MAIL_FROM = "pyrobots.teapot@gmail.com"
MAIL_PORT = 587
MAIL_SERVER = "smtp.gmail.com"
MAIL_FROM_NAME = "PyRobots Dev Team - 418 Teapot"

TOKEN_PREFIX = "localhost:8000/users/confirm"

mail_conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


def send_verification_token(e_mail: str, token: str):
    token_link = f"{TOKEN_PREFIX}?token={token}"

    e_mail_body = f"""
<span>
    <p>
        Por favor ingrese al siguiente link para verificar su usuario
        {token_link}
    </p>
</span>
"""

    message = MessageSchema(
        subject="Verificación de cuenta",
        recipients=[e_mail],
        body=e_mail_body,
        subtype=MessageType.html,
    )

    fm = FastMail(mail_conf)
    asyncio.run(fm.send_message(message))
