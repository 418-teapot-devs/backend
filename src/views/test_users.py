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
            "username was taken!",
        ),
        (
            {
                "username": "otrodistinto",
                "password": "salt27AAA!",
                "e_mail": "test@test.com",
            },
            "email was taken!",
        ),
        (
            {"username": "test", "password": "Aa12345678", "e_mail": "test@test.com"},
            "username was taken!",
        ),
    ]
    for params, expected_msg in test_jsons:
        response = cl.post("/users/", json=params)
        assert response.status_code == 422
        assert response.json() == {"detail": expected_msg}
