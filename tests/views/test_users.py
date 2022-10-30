from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.util.assets import ASSETS_DIR
from app.util.auth import JWT_ALGORITHM, JWT_SECRET_KEY

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

    data = response.json()
    assert "token" in data.keys()

    payload = jwt.decode(data["token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "login"
    assert payload["username"] == "test"

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
        "/users/login",
        json={"username": "leo10", "password": "Burrito21"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "token" in data.keys()

    payload = jwt.decode(data["token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "login"
    assert payload["username"] == "leo10"

    test_jsons = [
        (
            {"username": "leo11", "password": "Burrito21"},
            401,
            "username not found!",
        ),
        (
            {"username": "leo10", "password": "burrito21"},
            401,
            "passwords don't match!",
        ),
    ]

    for params, status_code, expected_msg in test_jsons:
        response = cl.post("/users/login", json=params)
        assert response.status_code == status_code


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
                open(f"{ASSETS_DIR}/robots/code/test_id_bot.py", "rb"),
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

    data = response.json()
    assert "token" in data.keys()

    payload = jwt.decode(data["token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "login"
    assert payload["username"] == "conavatar"
