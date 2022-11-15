from datetime import timedelta
from urllib.parse import quote_plus

from fastapi.testclient import TestClient

from pony.orm import db_session

from app.main import app
from app.models import Robot
from app.views.users import create_access_token
from tests.testutil import (
    create_random_robots,
    register_random_users,
)

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def test_create_robot():
    user = register_random_users(1)[0]
    token = user["token"]

    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )


    test_robots = [
            {"token": token, "name": "cesco", "code": "identity.py","expected_code": 201},
            {"token": token, "name": "cesco", "code": "identity.py", "expected_code": 409},
            {"token": fake_token, "name": "locke", "code": "identity.py", "expected_code": 404},
            ]

    for m in test_robots:
        files = []
        files.append(("code", m["code"]))

        files.append(("avatar", None))

        response = cl.post(
            f'/robots/?name={m["name"]}', headers={"token": m["token"]}, files=files
        )
        assert response.status_code == m["expected_code"]

        if m["expected_code"] == 201:
            with db_session:
                assert Robot.exists(name=m["name"])


def test_get_robots():
    user = {
        "username": "leotorres",
        "password": "AmoElQuartus21",
        "email": "leo@luis.tv",
    }

    response = cl.post(f"/users/{json_to_queryparams(user)}")
    assert response.status_code == 201

    data = response.json()
    token = data["token"]

    response = cl.get("/robots/", headers={"token": token})
    assert not list(response.json())

    test_robots = [
        ("locke", "identity.py", None),
        ("lueme", "identity.py", "identity_avatar.png"),
    ]

    for robot_name, code, avatar in test_robots:
        files = []
        files.append(("code", code))

        if avatar:
            files.append(("avatar", avatar))

        response = cl.post(
            f"/robots/?name={robot_name}", headers={"token": token}, files=files
        )
        assert response.status_code == 201

        response = cl.get("/robots/", headers={"token": token})
        robot = next(filter(lambda r: r["name"] == robot_name, list(response.json())))

        if robot["avatar_url"]:
            assert f"{robot['robot_id']}" in robot["avatar_url"]
        else:
            assert not robot["avatar_url"]
