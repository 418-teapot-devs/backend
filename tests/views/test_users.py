from datetime import timedelta
from filecmp import cmp
from os import path
from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from pony.orm import db_session

from app.main import app
from app.models.robot import Robot
from app.models.user import User
from app.util.assets import ASSETS_DIR, get_user_avatar
from app.util.auth import JWT_ALGORITHM, create_access_token, get_user_and_subject
from app.util.errors import *
from app.util.mail import (
    MAIL_FROM_NAME,
    MAIL_USERNAME,
    fm,
    send_recovery_mail,
    send_verification_token,
)
from tests.testutil import random_ascii_string, register_random_users

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def test_users_invalid_register():
    test_jsons = [
        {"username": "test", "password": "test"},
        {"username": "test", "email": "test@test.com"},
        {"username": "test", "password": "test", "email": "test"},
        {"username": "test", "password": "test", "email": "a@b.c"},
        {"username": "test", "password": "Test1234", "email": "a@bc"},
    ]
    for params in test_jsons:
        response = cl.post(f"/users/{json_to_queryparams(params)}")
        assert response.status_code == 422


def test_users_register_restrictions():
    params = json_to_queryparams(
        {"username": "test", "password": "418IAmATeapot", "email": "test@test.com"}
    )
    response = cl.post(f"/users/{params}")
    assert response.status_code == 201

    test_jsons = [
        (
            {
                "username": "test",
                "password": "pAssWord1",
                "email": "otro@distinto.com",
            },
            409,
            ["Username was taken!"],
        ),
        (
            {
                "username": "otrodistinto",
                "password": "salt27AAA!",
                "email": "test@test.com",
            },
            409,
            ["E-Mail was taken!"],
        ),
        (
            {"username": "test", "password": "Aa12345678", "email": "test@test.com"},
            409,
            ["Username was taken!", "E-Mail was taken!"],
        ),
    ]
    for params, status_code, expected_detail in test_jsons:
        response = cl.post(f"/users/{json_to_queryparams(params)}")
        assert response.status_code == status_code
        assert response.json() == {"detail": expected_detail}


def test_login():
    register_form = {
        "username": "leo10",
        "password": "Burrito21",
        "email": "leo10@hotemail.com.ar",
    }

    response = cl.post(f"/users/{json_to_queryparams(register_form)}")
    assert response.status_code == 201

    response = cl.post(
        "/users/login/",
        json={"username": "leo10", "password": "Burrito21"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "token" in data.keys()

    username, subject = get_user_and_subject(data["token"])
    assert subject == "login"
    assert username == register_form["username"]

    test_jsons = [
        (
            {"username": "leo11", "password": "Burrito21"},
            NON_EXISTANT_USER_OR_PASSWORD_ERROR.status_code,
            NON_EXISTANT_USER_OR_PASSWORD_ERROR.detail,
        ),
        (
            {"username": "leo10", "password": "burrito21"},
            NON_EXISTANT_USER_OR_PASSWORD_ERROR.status_code,
            NON_EXISTANT_USER_OR_PASSWORD_ERROR.detail,
        ),
    ]

    for params, status_code, expected_msg in test_jsons:
        response = cl.post("/users/login/", json=params)
        assert response.status_code == status_code


def test_send_mail():
    [user] = register_random_users(1)

    verify_token = create_access_token(
        {"sub": "verify", "username": user["username"]},
        timedelta(days=1.0),
    )

    with db_session:
        User[user["username"]].is_verified = False

    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        send_verification_token(user["email"], verify_token)
        send_recovery_mail(user["email"], verify_token)
        assert len(outbox) == 2
        assert outbox[0]["from"] == f"{MAIL_FROM_NAME} <{MAIL_USERNAME}>"
        assert outbox[1]["from"] == f"{MAIL_FROM_NAME} <{MAIL_USERNAME}>"
        assert outbox[0]["to"] == user["email"]
        assert outbox[1]["to"] == user["email"]


def test_invalid_verify():
    fake_tokens = [
        ("hola", INVALID_TOKEN_ERROR),
        (
            create_access_token(
                {"sub": "login", "user": "alvaro"}, timedelta(hours=1.0)
            ),
            INVALID_TOKEN_ERROR,
        ),
    ]

    for token, error in fake_tokens:
        response = cl.get(f"/users/verify/?token={token}")
        assert response.status_code == error.status_code
        assert response.json()["detail"] == error.detail


def test_verify():
    register_form = {
        "username": "Seba",
        "password": "Secr3tIs1m0#",
        "email": "sebastian.giraudo@mi.unc.edu.ar",
    }

    response = cl.post(f"/users/{json_to_queryparams(register_form)}")
    assert response.status_code == 201

    with db_session:
        user = User.get(name="Seba")
        user.is_verified = False

    login_form = {
        "username": register_form["username"],
        "password": register_form["password"],
    }
    response = cl.post("/users/login/", json=login_form)
    assert response.status_code == USER_NOT_VERIFIED_ERROR.status_code

    data = response.json()
    assert data["detail"] == USER_NOT_VERIFIED_ERROR.detail

    token_data = create_access_token(
        {"sub": "verify", "username": register_form["username"]},
        timedelta(hours=1.0),
    )

    response = cl.get(f"/users/verify/?token={token_data}")
    # cannot check status_code because it depends in frontend being mounted

    response = cl.post("/users/login/", json=login_form)
    assert response.status_code == 200


def test_users_avatar():
    json = {
        "username": "conavatar",
        "password": "Secr3tIs1m0#",
        "email": "img@test.com",
    }

    response = cl.post(
        f"/users/{json_to_queryparams(json)}",
        files={
            "avatar": (
                "imagen",
                open(f"{ASSETS_DIR}/defaults/code/test_id_bot.py", "rb"),
                "text/x-python",
            )
        },
    )
    assert response.status_code == 422

    response = cl.post(
        f"/users/{json_to_queryparams(json)}",
        files={
            "avatar": (
                "imagen",
                open(f"{ASSETS_DIR}/users/test.png", "rb"),
                "image/png",
            )
        },
    )
    assert response.status_code == 201


def test_default_robots():
    userdata = {
        "username": "leo", "password": "Burrito21", "email": "l@test.com"
    }
    response = cl.post(f"/users/{json_to_queryparams(userdata)}")
    assert response.status_code == 201

    userdata.pop('email')
    response = cl.post("/users/login/", json=userdata)
    assert response.status_code == 200

    data = response.json()
    token_header = {"token": data["token"]}

    with db_session:
        assert Robot.exists(name="default_1")

    expected_result = [
        {
            "robot_id": 1,
            "name": "default_1",
            "avatar_url": "/assets/avatars/robot/1.png",
            "won_matches": 0,
            "played_matches": 0,
            "mmr": 0,
        },
        {
            "robot_id": 2,
            "name": "default_2",
            "avatar_url": "/assets/avatars/robot/2.png",
            "won_matches": 0,
            "played_matches": 0,
            "mmr": 0,
        },
    ]

    response = cl.get("/robots/", headers=token_header)
    assert response.status_code == 200
    assert response.json() == expected_result
    assert path.exists(f"{ASSETS_DIR}/robots/code/1.py") and path.exists(
        f"{ASSETS_DIR}/robots/code/2.py"
    )
    assert path.exists(f"{ASSETS_DIR}/robots/avatars/1.png") and path.exists(
        f"{ASSETS_DIR}/robots/avatars/2.png"
    )
    assert cmp(
        f"{ASSETS_DIR}/robots/code/1.py", f"{ASSETS_DIR}/defaults/code/default_1.py"
    )
    assert cmp(
        f"{ASSETS_DIR}/robots/code/2.py", f"{ASSETS_DIR}/defaults/code/default_2.py"
    )


def test_invalid_get_profile():
    fake_tokens = [
        ("hola", INVALID_TOKEN_ERROR),
        (
            create_access_token(
                {"sub": "login", "user": "alvaro"}, timedelta(hours=1.0)
            ),
            INVALID_TOKEN_ERROR,
        ),
        (
            create_access_token(
                {"sub": "login", "username": "alvaro"}, timedelta(hours=1.0)
            ),
            USER_NOT_FOUND_ERROR,
        ),
    ]

    for token, error in fake_tokens:
        tok_header = {"token": token}

        response = cl.get("/users/profile/", headers=tok_header)
        assert response.status_code == error.status_code
        assert response.json()["detail"] == error.detail


def test_get_profile():
    user = register_random_users(1)[0]
    tok_header = {"token": user["token"]}

    response = cl.get("/users/profile/", headers=tok_header)

    assert response.status_code == 200
    assert response.json() == {
        "username": user["username"],
        "email": user["email"],
        "avatar_url": None,
    }


def test_invalid_patch_profile():
    fake_token = create_access_token(
        {"sub": "login", "username": "alvaro"}, timedelta(hours=1.0)
    )
    tok_header = {"token": fake_token}

    response = cl.patch(
        f"/users/profile/",
        headers=tok_header,
        files={
            "avatar": (
                "imagen",
                open(f"{ASSETS_DIR}/users/test.png", "rb"),
                "image/png",
            )
        },
    )
    assert response.status_code == USER_NOT_FOUND_ERROR.status_code

    user = register_random_users(1)[0]
    tok_header = {"token": user["token"]}

    response = cl.patch(
        f"/users/profile/",
        headers=tok_header,
        files={
            "avatar": (
                "imagen",
                open(f"{ASSETS_DIR}/defaults/code/test_id_bot.py", "rb"),
                "text/x-python",
            )
        },
    )
    assert response.status_code == INVALID_PICTURE_FORMAT_ERROR.status_code


def test_patch_profile():
    user = register_random_users(1)[0]
    tok_header = {"token": user["token"]}

    response = cl.patch(
        f"/users/profile/",
        headers=tok_header,
        files={
            "avatar": (
                "imagen",
                open(f"{ASSETS_DIR}/users/test.png", "rb"),
                "image/png",
            )
        },
    )

    with db_session:
        user_db = User.get(name=user["username"])

    new_avatar_url = get_user_avatar(user_db)

    assert response.status_code == 200
    assert response.json() == {
        "username": user["username"],
        "email": user["email"],
        "avatar_url": new_avatar_url,
    }
    assert user_db.has_avatar
    assert cmp(
        f'{ASSETS_DIR}/users/{user["username"]}.png', f"{ASSETS_DIR}/users/test.png"
    )


def test_invalid_put_password():
    fake_token = create_access_token(
        {"sub": "login", "username": "alvaro"}, timedelta(hours=1.0)
    )
    tok_header = {"token": fake_token}

    response = cl.put(
        "/users/password/",
        headers=tok_header,
        json={"old_password": "estaN0Es", "new_password": "Burrito429"},
    )
    assert response.status_code == USER_NOT_FOUND_ERROR.status_code

    params = {
        "username": "maciel",
        "password": "Burrito21",
        "email": "midulcelechona@test.com",
    }
    response = cl.post(f"/users/{json_to_queryparams(params)}")
    assert response.status_code == 201

    params.pop('email')
    response = cl.post("/users/login/", json=params)
    assert response.status_code == 200

    data = response.json()
    tok_header = {"token": data["token"]}
    response = cl.put(
        "/users/password/",
        headers=tok_header,
        json={"old_password": "estaN0Es", "new_password": "Burrito429"},
    )
    assert response.status_code == NON_EXISTANT_USER_OR_PASSWORD_ERROR.status_code

    params = json_to_queryparams(
        {
            "username": "maciel",
            "password": "burrito",
            "email": "midulcelechona@test.com",
        }
    )
    response = cl.post(f"/users/{params}")
    assert response.status_code == VALUE_NOT_VALID_PASSWORD.status_code

    response = cl.put(
        "/users/password/",
        headers=tok_header,
        json={"old_password": "Burrito21", "new_password": "Burrito21"},
    )
    assert response.status_code == CURRENT_PASSWORD_EQUAL_NEW_PASSWORD.status_code


def test_put_password():
    params = {
        "username": "maciel",
        "password": "Burrito21",
        "email": "midulcelechona@test.com",
    }
    response = cl.post(f"/users/{json_to_queryparams(params)}")
    assert response.status_code == 201

    params.pop('email')
    response = cl.post("/users/login/", json=params)
    assert response.status_code == 200

    data = response.json()
    tok_header = {"token": data["token"]}
    response = cl.put(
        "/users/password/",
        headers=tok_header,
        json={"old_password": "Burrito21", "new_password": "Burrito429"},
    )
    assert response.status_code == 200

    response = cl.post(
        "/users/login/",
        json={
            "username": "maciel",
            "password": "Burrito21",
            "email": "midulcelechona@test.com",
        },
    )
    assert response.status_code == NON_EXISTANT_USER_OR_PASSWORD_ERROR.status_code

    response = cl.post(
        "/users/login/",
        json={
            "username": "maciel",
            "password": "Burrito429",
            "email": "midulcelechona@test.com",
        },
    )
    assert response.status_code == 200


def test_reset_password_bad_token():
    [user] = register_random_users(1)

    recover_token = create_access_token(
        {"sub": "login", "username": user["username"]},
        timedelta(hours=1.0),
    )

    # try to recover using old password
    response = cl.put(
        "/users/reset_password/",
        headers={"token": recover_token},
        json={"new_password": "Aa123456"},
    )
    assert response.status_code == INVALID_TOKEN_ERROR.status_code
    assert response.json()["detail"] == INVALID_TOKEN_ERROR.detail


def test_recover_password_invalid_pwd():
    [user] = register_random_users(1)

    recover_token = create_access_token(
        {"sub": "recovery", "username": user["username"]},
        timedelta(hours=1.0),
    )

    # try to recover using old password
    response = cl.put(
        "/users/reset_password/",
        headers={"token": recover_token},
        json={"new_password": "soup"},
    )
    assert response.status_code == 422


def test_recover_password():
    register_form = {
        "username": "alvaro",
        "password": f"1Aa{random_ascii_string(5)}",
        "email": "alvaro.schachner@mi.unc.edu.ar",
    }

    response = cl.post(f"/users/{json_to_queryparams(register_form)}")
    assert response.status_code == 201

    # try to use email that isn't from any user
    response = cl.put("/users/recover/", json={"email": "a@b.c"})
    assert response.status_code == EMAIL_DOESNT_BELONG_TO_USER.status_code
    assert response.json()["detail"] == EMAIL_DOESNT_BELONG_TO_USER.detail

    response = cl.put("/users/recover/", json={"email": register_form["email"]})
    assert response.status_code == 200

    recover_token = create_access_token(
        {"sub": "recovery", "username": register_form["username"]},
        timedelta(hours=1.0),
    )

    # try to recover using old password
    response = cl.put(
        "/users/reset_password/",
        headers={"token": recover_token},
        json={"new_password": register_form["password"]},
    )
    assert response.status_code == CURRENT_PASSWORD_EQUAL_NEW_PASSWORD.status_code
    assert response.json()["detail"] == CURRENT_PASSWORD_EQUAL_NEW_PASSWORD.detail

    password = "Aa123456"
    response = cl.put(
        "/users/reset_password/",
        headers={"token": recover_token},
        json={"new_password": password},
    )
    assert response.status_code == 200

    # try to login using already changed old password
    response = cl.post(
        "/users/login/",
        json={
            "username": register_form["username"],
            "password": register_form["password"],
        },
    )
    assert response.status_code == 401

    response = cl.post(
        "/users/login/",
        json={"username": register_form["username"], "password": password},
    )
    assert response.status_code == 200
