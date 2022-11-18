import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

MAIL_USERNAME = "pyrobots.teapot@gmail.com"
MAIL_PASSWORD = "lbyqdaxqkwfhhpcp"
MAIL_FROM = "pyrobots.teapot@gmail.com"
MAIL_PORT = 587
MAIL_SERVER = "smtp.gmail.com"
MAIL_FROM_NAME = "PyRobots Dev Team - 418 Teapot"

TOKEN_PREFIX = "http://localhost:8000/users/verify/"

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
    VALIDATE_CERTS=True,
)

fm = FastMail(mail_conf)


def send_verification_token(e_mail: str, token: str):
    token_link = f"{TOKEN_PREFIX}?token={token}"

    with open("app/util/verify_mail.html", "r") as body:
        email_body = body.read().replace("\n", "").format(token=token_link)

    message = MessageSchema(
        subject="Verificación de cuenta",
        recipients=[e_mail],
        body=email_body,
        subtype=MessageType.html,
    )

    asyncio.run(fm.send_message(message))
