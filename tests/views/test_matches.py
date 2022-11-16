from datetime import timedelta

from fastapi.testclient import TestClient
from pony.orm import commit, db_session

from app.main import app
from app.models import Match, Robot, RobotMatchResult
from app.util.auth import create_access_token
from app.util.errors import *
from tests.testutil import (
    create_random_matches,
    create_random_robots,
    json_to_queryparams,
    register_random_users,
)

cl = TestClient(app)


def test_create_from_nonexistant_user():

    fake_token = create_access_token(
        {"sub": "login", "username": "leo"}, timedelta(hours=1.0)
    )

    test_match = {
        "name": "string",
        "robot_id": 0,
        "max_players": 0,
        "min_players": 0,
        "rounds": 0,
        "games": 0,
        "password": "string",
    }

    response = cl.post("/matches/", headers={"token": fake_token}, json=test_match)
    assert response.status_code == USER_NOT_FOUND_ERROR.status_code


def test_get_from_nonexistant_user():
    fake_token = create_access_token(
        {"sub": "login", "username": "leo"}, timedelta(hours=1.0)
    )

    response = cl.get("/matches/1", headers={"token": fake_token})
    assert response.status_code == USER_NOT_FOUND_ERROR.status_code


def test_get_with_qp_from_nonexistant_user():
    fake_token = create_access_token(
        {"sub": "login", "username": "leo"}, timedelta(hours=1.0)
    )

    response = cl.get("/matches/?match_type=created", headers={"token": fake_token})
    assert response.status_code == USER_NOT_FOUND_ERROR.status_code


def test_get_nonexistent_match():
    user = {"username": "gino", "password": "GatoTruco123", "email": "k@gmail.com"}

    response = cl.post(f"/users/{json_to_queryparams(user)}")
    assert response.status_code == 201

    token = response.json()["token"]

    response = cl.get("/matches/1", headers={"token": token})
    assert response.status_code == MATCH_NOT_FOUND_ERROR.status_code


def test_created_invalid_match():
    users = register_random_users(2)
    robots = []
    for i in range(2):
        robots.append(create_random_robots(users[i]["token"], 1)[0])

    matches = [
        {
            "token": users[0]["token"],
            "name": "partida1",
            "robot_id": 3,
            "max_players": 4,
            "min_players": 2,
            "rounds": 10000,
            "games": 200,
            "password": "algo",
            "expected_code": ROBOT_NOT_FOUND_ERROR.status_code,
        },
        {
            "token": users[1]["token"],
            "name": "partida1",
            "robot_id": 1,
            "max_players": 4,
            "min_players": 2,
            "rounds": 10000,
            "games": 200,
            "password": "algo",
            "expected_code": 401,
        },
    ]

    for m in matches:
        response = cl.post("/matches/", headers={"token": m["token"]}, json=m)

        assert response.status_code == m["expected_code"]


def test_post_created():
    users = register_random_users(2)
    robots = []
    for i in range(2):
        robots.append(create_random_robots(users[i]["token"], 1)[0])

    matches = [
        {
            "token": users[0]["token"],
            "name": "partida1",
            "robot_id": 1,
            "max_players": 4,
            "min_players": 2,
            "rounds": 10000,
            "games": 200,
            "password": "algo",
            "expected_code": 201,
        },
        {
            "token": users[1]["token"],
            "name": "partida2",
            "robot_id": 2,
            "max_players": 4,
            "min_players": 2,
            "rounds": 10000,
            "games": 200,
            "password": "algo",
            "expected_code": 201,
        },
    ]

    for m in matches:
        response = cl.post("/matches/", headers={"token": m["token"]}, json=m)
        assert response.status_code == m["expected_code"]

        with db_session:
            assert Match.exists(name=m["name"])


def test_get_created():
    users = register_random_users(2)
    matches = create_random_matches(users[0]["token"], 2)

    with db_session:
        m1 = Match.get(id=matches[0]["id"])
        m2 = Match.get(id=matches[1]["id"])
        r1 = list(m1.plays)[0]
        r2 = list(m2.plays)[0]
        get_matches = [
            {
                "name": m1.name,
                "id": m1.id,
                "host": {"username": users[0]["username"], "avatar_url": None},
                "max_players": 4,
                "min_players": 2,
                "games": m1.game_count,
                "rounds": m1.round_count,
                "is_private": True,
                "robots": {
                    f"{r1.id}": {
                        "name": r1.name,
                        "avatar_url": None,
                        "username": users[0]["username"],
                    }
                },
                "state": "Lobby",
                "results": None,
            },
            {
                "name": m2.name,
                "id": m2.id,
                "host": {"username": users[0]["username"], "avatar_url": None},
                "max_players": 4,
                "min_players": 2,
                "games": m2.game_count,
                "rounds": m2.round_count,
                "is_private": True,
                "robots": {
                    f"{r2.id}": {
                        "name": r2.name,
                        "avatar_url": None,
                        "username": users[0]["username"],
                    }
                },
                "state": "Lobby",
                "results": None,
            },
        ]

    response = cl.get(
        "/matches/?match_type=created", headers={"token": users[0]["token"]}
    )
    assert response.status_code == 200

    response = cl.get(
        "/matches/?match_type=created", headers={"token": users[0]["token"]}
    )
    assert response.status_code == 200
    assert response.json() == get_matches


def test_join_nonexistant_match():
    user = register_random_users(1)[0]
    robot = create_random_robots(user["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": ""}
    tok_header = {"token": user["token"]}

    response = cl.put("/matches/1/join/", headers=tok_header, json=json_form)
    assert response.status_code == MATCH_NOT_FOUND_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_NOT_FOUND_ERROR.detail


def test_join_match_nonexistant_robot():
    user = register_random_users(1)[0]
    match = create_random_matches(user["token"], 1)[0]

    json_form = {"robot_id": 100000000, "password": match["password"]}
    tok_header = {"token": user["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == ROBOT_NOT_FOUND_ERROR.status_code

    data = response.json()
    assert data["detail"] == ROBOT_NOT_FOUND_ERROR.detail


def test_join_match_unowned_robot():
    users = register_random_users(2)
    robot = create_random_robots(users[0]["token"], 1)[0]
    match = create_random_matches(users[0]["token"], 1)[0]

    # robot id from first user, token from second
    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == ROBOT_NOT_FROM_USER_ERROR.status_code

    data = response.json()
    assert data["detail"] == ROBOT_NOT_FROM_USER_ERROR.detail


def test_join_match_already_started():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    # for second user
    robot = create_random_robots(users[1]["token"], 1)[0]

    with db_session:
        m = Match[match["id"]]
        m.state = "Started"
        commit()

    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == MATCH_STARTED_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_STARTED_ERROR.detail


def test_join_full_match():
    users = register_random_users(5)

    robots = []
    for user in users:
        robots.append(create_random_robots(user["token"], 1)[0])

    match = create_random_matches(users[0]["token"], 1)[0]

    for i, user in enumerate(users[1:-1], start=1):
        json_form = {"robot_id": robots[i]["id"], "password": match["password"]}
        tok_header = {"token": user["token"]}

        response = cl.put(
            f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
        )
        assert response.status_code == 201

    json_form = {"robot_id": robots[4]["id"], "password": match["password"]}
    tok_header = {"token": users[4]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == MATCH_FULL_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_FULL_ERROR.detail


def test_join_match_invalid_password():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    robot = create_random_robots(users[1]["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": "1" + match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == MATCH_PASSWORD_INCORRECT_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_PASSWORD_INCORRECT_ERROR.detail


def test_join_matches_empty_password():
    users = register_random_users(2)

    robots = []
    for user in users:
        robots.append(create_random_robots(user["token"], 1)[0])

    response = cl.post(
        "/matches/",
        headers={"token": users[0]["token"]},
        json={
            "name": "bg1!",
            "robot_id": robots[0]["id"],
            "max_players": 4,
            "min_players": 2,
            "rounds": 10000,
            "games": 150,
            "password": "",
        },
    )
    assert response.status_code == 201

    json_form = {"robot_id": robots[1]["id"], "password": ""}
    tok_header = {"token": users[1]["token"]}

    response = cl.put("/matches/1/join/", headers=tok_header, json=json_form)
    assert response.status_code == 201


def test_join_match():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    robot = create_random_robots(users[1]["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == 201

    response = cl.get(f"/matches/{match['id']}", headers=tok_header)
    assert response.status_code == 200

    data = response.json()
    assert str(data["id"]) == match["id"]
    assert any(
        robot["name"] == robot_in_match["name"]
        for robot_in_match in data["robots"].values()
    )

    response = cl.get("/matches/?match_type=public", headers=tok_header)
    data = response.json()
    assert len(data) == len(set(m["id"] for m in data))


def test_join_matches_replacing_robot():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    robot = create_random_robots(users[1]["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == 201

    response = cl.get(f"/matches/{match['id']}", headers=tok_header)
    assert response.status_code == 200

    data = response.json()
    assert str(data["id"]) == match["id"]
    assert any(
        robot["name"] == robot_in_match["name"]
        for robot_in_match in data["robots"].values()
    )

    # joining with a new robot must replace the old one
    new_robot = create_random_robots(users[1]["token"], 1)[0]

    json_form = {"robot_id": new_robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == 201

    response = cl.get(f"/matches/{match['id']}", headers=tok_header)
    assert response.status_code == 200

    data = response.json()
    assert str(data["id"]) == match["id"]
    assert all(
        robot["name"] != robot_in_match["name"]
        for robot_in_match in data["robots"].values()
    )
    assert any(new_robot["name"] == robot["name"] for robot in data["robots"].values())


def test_leave_nonexistant_match():
    user = register_random_users(1)[0]

    tok_header = {"token": user["token"]}

    response = cl.put("/matches/1/leave/", headers=tok_header)
    assert response.status_code == MATCH_NOT_FOUND_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_NOT_FOUND_ERROR.detail


def test_leave_not_joined_match():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    tok_header = {"token": users[1]["token"]}

    response = cl.put(f"/matches/{match['id']}/leave/", headers=tok_header)
    assert response.status_code == USER_WAS_NOT_IN_MATCH_ERROR.status_code

    data = response.json()
    assert data["detail"] == USER_WAS_NOT_IN_MATCH_ERROR.detail


def test_leave_match_from_host():
    user = register_random_users(1)[0]
    match = create_random_matches(user["token"], 1)[0]

    tok_header = {"token": user["token"]}

    response = cl.put(f"/matches/{match['id']}/leave/", headers=tok_header)
    assert response.status_code == MATCH_CANNOT_BE_LEFT_BY_HOST_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_CANNOT_BE_LEFT_BY_HOST_ERROR.detail


def test_leave_started_match():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    robot = create_random_robots(users[1]["token"], 1)[0]

    tok_header = {"token": users[1]["token"]}
    json_form = {"robot_id": robot["id"], "password": match["password"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == 201

    with db_session:
        m = Match[match["id"]]
        m.state = "Started"
        commit()

    response = cl.put(f"/matches/{match['id']}/leave/", headers=tok_header)
    assert response.status_code == MATCH_STARTED_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_STARTED_ERROR.detail


def test_leave_match():
    users = register_random_users(2)
    robot = create_random_robots(users[1]["token"], 1)[0]

    match = create_random_matches(users[0]["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(
        f"/matches/{match['id']}/join/", headers=tok_header, json=json_form
    )
    assert response.status_code == 201

    response = cl.get(f"/matches/{match['id']}", headers=tok_header)
    assert response.status_code == 200

    data = response.json()
    assert str(data["id"]) == match["id"]
    assert any(
        robot["name"] == robot_in_match["name"]
        for robot_in_match in data["robots"].values()
    )

    response = cl.put(f"/matches/{match['id']}/leave/", headers=tok_header)
    assert response.status_code == 201

    response = cl.get(f"/matches/{match['id']}", headers=tok_header)
    assert response.status_code == 200

    data = response.json()
    assert str(data["id"]) == match["id"]
    assert all(
        robot["name"] != robot_in_match["name"]
        for robot_in_match in data["robots"].values()
    )


def test_start_match():
    users = register_random_users(2)
    tok_header = {"token": users[0]["token"]}

    robots = []
    for user in users:
        robots.append(create_random_robots(user["token"], 1)[0])

    # match = create_random_matches(users[0]["token"], 1)[0]

    json_header = {
        "name": "partida1",
        "robot_id": robots[0]["id"],
        "max_players": 4,
        "min_players": 2,
        "rounds": 10,
        "games": 1,
        "password": "123",
    }

    response = cl.post("/matches/", headers=tok_header, json=json_header)
    assert response.status_code == 201

    with db_session:
        m = Match.get(id=1)
        m.plays.add(Robot.get(id=robots[1]["id"]))
        commit()

    response = cl.put("/matches/1/start/", headers=tok_header)

    assert response.status_code == 201

    with db_session:
        assert RobotMatchResult.exists(robot_id=robots[0]["id"], match_id=1)
        assert RobotMatchResult.exists(robot_id=robots[1]["id"], match_id=1)

    with db_session:
        m = Match.get(id=1)
        assert m.state == "Finished"


def test_start_nonexistant_user():
    fake_token = create_access_token(
        {"sub": "login", "username": "leo"}, timedelta(hours=1.0)
    )

    response = cl.put("/matches/1/start/", headers={"token": fake_token})
    assert response.status_code == USER_NOT_FOUND_ERROR.status_code


def test_start_nonexistant_match():
    user = register_random_users(1)[0]

    tok_header = {"token": user["token"]}

    response = cl.put("/matches/1/start/", headers=tok_header)
    assert response.status_code == MATCH_NOT_FOUND_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_NOT_FOUND_ERROR.detail


def test_start_match_already_started():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    with db_session:
        m = Match[match["id"]]
        m.state = "InGame"
        commit()

    tok_header = {"token": users[1]["token"]}

    response = cl.put(f"/matches/{match['id']}/start/", headers=tok_header)
    assert response.status_code == MATCH_STARTED_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_STARTED_ERROR.detail


def test_start_match_unowned_robot():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    # robot id from first user, token from second
    tok_header = {"token": users[1]["token"]}

    response = cl.put(f"/matches/{match['id']}/start/", headers=tok_header)
    assert response.status_code == MATCH_CAN_ONLY_BE_STARTED_BY_HOST_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_CAN_ONLY_BE_STARTED_BY_HOST_ERROR.detail


def test_start_match_maximum():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    # for second user
    robots = create_random_robots(users[0]["token"], 5)

    with db_session:
        m = Match[match["id"]]

        for r in robots:
            m.plays.add(Robot.get(id=r["id"]))
        commit()

    tok_header = {"token": users[0]["token"]}

    response = cl.put(f"/matches/{match['id']}/start/", headers=tok_header)
    assert response.status_code == MATCH_FULL_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_FULL_ERROR.detail


def test_start_match_minimum():
    users = register_random_users(1)
    match = create_random_matches(users[0]["token"], 1)[0]

    tok_header = {"token": users[0]["token"]}

    response = cl.put(f"/matches/{match['id']}/start/", headers=tok_header)
    assert response.status_code == MATCH_MINIMUM_PLAYERS_NOT_REACHED_ERROR.status_code

    data = response.json()
    assert data["detail"] == MATCH_MINIMUM_PLAYERS_NOT_REACHED_ERROR.detail
