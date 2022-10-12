from fastapi.testclient import TestClient
from jose import jwt

from ..main import app
from ..views import JWT_ALGORITHM, JWT_SECRET_KEY

cl = TestClient(app)


def test_users_invalid_register():
    test_jsons = [
        {"username": "test", "password": "test"},
        {"username": "test", "e_mail": "test@test.com"},
        {"username": "test", "password": "test", "e_mail": "test"},
        {"username": "test", "password": "test", "e_mail": "a@b.c"},
        {"username": "test", "password": "Test1234", "e_mail": "a@bc"},
    ]
    for params in test_jsons:
        response = cl.post("/users/", json=params)
        assert response.status_code == 422


def test_users_register_restrictions():
    response = cl.post(
        "/users/",
        json={
            "username": "test",
            "password": "418IAmATeapot",
            "e_mail": "test@test.com",
        },
    )
    assert response.status_code == 200

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
                "e_mail": "otro@distinto.com",
            },
            422,
            "username was taken!",
        ),
        (
            {
                "username": "otrodistinto",
                "password": "salt27AAA!",
                "e_mail": "test@test.com",
            },
            422,
            "email was taken!",
        ),
        (
            {"username": "test", "password": "Aa12345678", "e_mail": "test@test.com"},
            422,
            "username was taken!",
        ),
    ]
    for params, status_code, expected_msg in test_jsons:
        response = cl.post("/users/", json=params)
        assert response.status_code == status_code
        assert response.json() == {"detail": expected_msg}


def test_login():
    response = cl.post(
        "/users/",
        json={
            "username": "leo10",
            "password": "Burrito21",
            "e_mail": "leo10@hotmail.com.ar",
        },
    )
    assert response.status_code == 200

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
        assert response.json() == {"detail": expected_msg}
