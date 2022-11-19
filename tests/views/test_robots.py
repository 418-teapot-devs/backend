from datetime import timedelta
from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from pony.orm import db_session

from app.main import app
from app.models import Robot
from app.views.users import create_access_token
from tests.testutil import create_random_robots, register_random_users

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
        {"token": token, "name": "cesco", "code": "identity.py", "expected_code": 201},
        {"token": token, "name": "cesco", "code": "identity.py", "expected_code": 409},
        {
            "token": fake_token,
            "name": "locke",
            "code": "identity.py",
            "expected_code": 404,
        },
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
    user = register_random_users(2)

    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )

    response = cl.get("/robots/", headers={"token": fake_token})
    assert response.status_code == 404

    robots_u1 = create_random_robots(user[0]["token"], 2)
    robots_u2 = create_random_robots(user[1]["token"], 1)

    test_robots = [
        [

            {
                "robot_id": int(robots_u1[0]["id"]),
                "name": robots_u1[0]["name"],
                "avatar_url": None,
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },
            {
                "robot_id": int(robots_u1[1]["id"]),
                "name": robots_u1[1]["name"],
                "avatar_url": None,
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },
            {
                "robot_id": 1,
                "name": "default_1",
                "avatar_url": "/assets/avatars/robot/1.png",
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },           {
                "robot_id": 2,
                "name": "default_2",
                "avatar_url": "/assets/avatars/robot/2.png",
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },
        ],
        [
            {
                "robot_id": int(robots_u2[0]["id"]),
                "name": robots_u2[0]["name"],
                "avatar_url": None,
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },
            {
                "robot_id": 3,
                "name": "default_1",
                "avatar_url": "/assets/avatars/robot/3.png",
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },
            {
                "robot_id": 4,
                "name": "default_2",
                "avatar_url": "/assets/avatars/robot/4.png",
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            },

        ],
    ]

    for i, r in enumerate(test_robots):
        response = cl.get("/robots/", headers={"token": user[i]["token"]})
        assert response.json() == r
