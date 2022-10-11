from fastapi import responses
from fastapi.testclient import TestClient

from ..main import app

cl = TestClient(app)


def test_users_invalid_register():
    test_jsons = [
        {"username": "test", "password": "test"},
        {"username": "test", "e_mail": "test@test.com"},
        {"username": "test", "password": "test", "e_mail": "test"},
        {"username": "test", "password": "test"},
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
    assert response.json() == {}

    test_jsons = [
        (
            {
                "username": "test",
                "password": "pAssWord1",
                "e_mail": "otro@distinto.com",
            },
            "Username was taken!",
        ),
        (
            {
                "username": "otrodistinto",
                "password": "salt27AAA!",
                "e_mail": "test@test.com",
            },
            "E-Mail was taken!",
        ),
        (
            {"username": "test", "password": "Aa12345678", "e_mail": "test@test.com"},
            "Username was taken!",
        ),
    ]
    for params, expected_msg in test_jsons:
        response = cl.post("/users/", json=params)
        assert response.status_code == 422
        assert response.json() == {"detail": expected_msg}
