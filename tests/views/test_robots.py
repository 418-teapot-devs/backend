from datetime import timedelta
from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from pony.orm import db_session

from app.main import app
from app.models import Robot
from app.views.users import create_access_token
from app.models.robot import Robot
from tests.testutil import register_random_users, create_random_robots, create_random_matches

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
        ],
        [
            {
                "robot_id": int(robots_u2[0]["id"]),
                "name": robots_u2[0]["name"],
                "avatar_url": None,
                "won_matches": 0,
                "played_matches": 0,
                "mmr": 0,
            }
        ],
    ]

    for i, r in enumerate(test_robots):
        response = cl.get("/robots/", headers={"token": user[i]["token"]})
        assert response.json() == r


def test_robot_results():
    host, *players = register_random_users(4)

    create_random_robots(host["token"], 33)
    match = create_random_matches(host["token"], 1)[0]

    for player in players:
        player["robot"] = create_random_robots(player["token"], 1)[0]

        join_form = {"robot_id": player["robot"]["id"], "password": match["password"]}
        token_header = {"token": player["token"]}

        response = cl.put(f"/matches/{match['id']}/join/", headers=token_header, json=join_form)
        assert response.status_code == 201

    host_token_header = {"token": host["token"]}
    response = cl.put(f"/matches/{match['id']}/start/", headers=host_token_header)
    assert response.status_code == 201

    match_result = cl.get(f"/matches/{match['id']}/", headers=host_token_header).json()
    for robot_id in match_result["robots"]:
        robot_result = match_result["results"][robot_id]

        expected_mmr = 0
        expected_won_matches = 0
        if robot_result["robot_pos"] == 1:
            expected_mmr = 20
            expected_won_matches = 1

        with db_session:
            robot = Robot[robot_id]

        assert robot.played_matches == 1
        assert robot.mmr == expected_mmr
        assert robot.won_matches == expected_won_matches
