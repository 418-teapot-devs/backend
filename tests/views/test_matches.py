from datetime import timedelta

from fastapi.testclient import TestClient
from pony.orm import db_session, commit

from app.main import app
from app.util.auth import create_access_token
from app.models.match import Match
from tests.testutil import register_random_users, create_random_robots, create_random_matches, json_to_queryparams

cl = TestClient(app)


def test_create_from_nonexistant_user():
    fake_token = create_access_token(
        {"sub": "login", "username": "leo"},
        timedelta(hours=1.0)
    )

    test_match = {
        "name": "string",
        "robot_id": 0,
        "max_players": 0,
        "min_players": 0,
        "rounds": 0,
        "games": 0,
        "password": "string"
    }

    response = cl.post("/matches/", headers={"token": fake_token}, json=test_match)
    assert response.status_code == 404


def test_get_from_nonexistant_user():
    fake_token = create_access_token(
        {"sub": "login", "username": "leo"},
        timedelta(hours=1.0)
    )

    response = cl.get("/matches/1", headers={"token": fake_token})
    assert response.status_code == 404


def test_get_with_qp_from_nonexistant_user():
    fake_token = create_access_token(
        {"sub": "login", "username": "leo"},
        timedelta(hours=1.0)
    )

    response = cl.get("/matches/?match_type=created", headers={"token": fake_token})
    assert response.status_code == 404


def test_get_nonexistent_match():
    user = {"username": "gino", "password": "GatoTruco123", "email": "k@gmail.com"}

    response = cl.post(f"/users/{json_to_queryparams(user)}")
    assert response.status_code == 201

    token = response.json()["token"]

    response = cl.get("/matches/1", headers={"token": token})
    assert response.status_code == 404


def test_created_invalid_match():
    users = [
        {
            "username": "alvaro",
            "password": "MILC(man,i love ceimaf)123",
            "email": "a@gemail.com",
        },
        {
            "username": "bruno",
            "password": "h0la soy del Monse",
            "email": "b@gemail.com",
        },
        {"username": "leo", "password": "Burrito21", "email": "l@gemail.com"},
    ]

    tokens = {}
    for user in users:
        response = cl.post(f"/users/{json_to_queryparams(user)}")
        assert response.status_code == 201

        data = response.json()
        tokens[user["username"]] = data["token"]

    test_robots = [
        ("daneel R olivaw", tokens["leo"], "identity.py", None, 201),
        ("R giskard", tokens["leo"], "identity.py", None, 201),
        ("Marvin", tokens["bruno"], "identity.py", None, 201),
        ("deep thought", tokens["alvaro"], "identity.py", None, 201),
    ]

    for robot_name, token, code, avatar, expected_code in test_robots:
        response = cl.post(
            f"/robots/?name={robot_name}",
            headers={"token": token},
            files=[("code", code)],
        )

        assert response.status_code == expected_code

    test_matches = [
        (
            "fadsfasdfasdfasdfasdfa",
            "partida1",
            "3",
            2,
            4,
            10000,
            200,
            "algo",
            401,
        ),
        (
            tokens["bruno"],
            "partida1",
            "5134",
            2,
            4,
            10000,
            200,
            "algo",
            404,
        ),
        (
            tokens["bruno"],
            "partida1",
            "1",
            2,
            4,
            10000,
            200,
            "algo",
            401,
        ),
    ]

    for (
        token,
        m_name,
        r_id,
        min_p,
        max_p,
        games,
        rounds,
        password,
        expected_code,
    ) in test_matches:
        response = cl.post(
            "/matches/",
            headers={"token": token},
            json={
                "name": m_name,
                "robot_id": r_id,
                "max_players": min_p,
                "min_players": max_p,
                "rounds": rounds,
                "games": games,
                "password": password,
            },
        )

        assert response.status_code == expected_code


def test_post_created():
    users = [
        {"username": "bash", "password": "Reg2Loc_a", "email": "a1@gemail.com"},
        {
            "username": "bruno1",
            "password": "h0la soy del Monse",
            "email": "b1@gemail.com",
        },
        {
            "username": "leo1",
            "password": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "email": "l1@gemail.com",
        },
    ]

    tokens = {}
    for user in users:
        response = cl.post(f"/users/{json_to_queryparams(user)}")
        assert response.status_code == 201
        data = response.json()

        tokens[user["username"]] = data["token"]

    test_robots = [
        ("Raichu", tokens["leo1"], "identity.py", None, 201),
        ("Zubat", tokens["leo1"], "identity.py", None, 201),
        ("Moltres", tokens["bruno1"], "identity.py", None, 201),
        ("Ribombee", tokens["bash"], "identity.py", None, 201),
    ]

    for robot_name, token, code, avatar, expected_code in test_robots:
        response = cl.post(
            f"/robots/?name={robot_name}",
            headers={"token": token},
            files=[("code", code)],
        )

        assert response.status_code == expected_code

    test_matches = [
        (
            tokens["bruno1"],
            "partida1",
            3,
            2,
            4,
            10000,
            200,
            "algo",
            201,
        ),
        (
            tokens["leo1"],
            "partida2",
            1,
            2,
            4,
            5000,
            100,
            "algo",
            201,
        ),
        (tokens["leo1"], "partida3", 2, 3, 4, 8540, 2, "algo", 201),
    ]

    for (
        token,
        m_name,
        robot_id,
        min_p,
        max_p,
        games,
        rounds,
        password,
        expected_code,
    ) in test_matches:
        response = cl.post(
            "/matches/",
            headers={"token": token},
            json={
                "name": m_name,
                "robot_id": robot_id,
                "max_players": max_p,
                "min_players": min_p,
                "rounds": rounds,
                "games": games,
                "password": password,
            },
        )

        assert response.status_code == expected_code


def test_get_created():
    users = [
        {
            "username": "alvaro2",
            "password": "MILC(man,i love ceimaf)123",
            "email": "a2@gemail.com",
        },
        {
            "username": "bruno2",
            "password": "h0la soy del Monse",
            "email": "b2@gemail.com",
        },
        {"username": "leo2", "password": "Burrito21", "email": "l2@gemail.com"},
    ]

    tokens = {}
    for user in users:
        response = cl.post(f"/users/{json_to_queryparams(user)}")
        assert response.status_code == 201
        data = response.json()

        tokens[user["username"]] = data["token"]

    test_robots = [
        ("daneel R olivaw", tokens["leo2"], "identity.py", None, 201),
        ("R giskard", tokens["leo2"], "identity.py", None, 201),
        ("Marvin", tokens["bruno2"], "identity.py", None, 201),
        ("deep thought", tokens["alvaro2"], "identity.py", None, 201),
    ]

    for robot_name, token, code, avatar, expected_code in test_robots:
        response = cl.post(
            f"/robots/?name={robot_name}",
            headers={"token": token},
            files=[("code", code)],
        )

        assert response.status_code == expected_code

    test_matches = [
        (
            tokens["bruno2"],
            "partida0",
            3,
            2,
            4,
            10000,
            200,
            "algo",
            201,
        ),
        (
            tokens["bruno2"],
            "partida1",
            3,
            2,
            4,
            10000,
            200,
            "algo",
            201,
        ),
        (
            tokens["leo2"],
            "partida2",
            1,
            2,
            4,
            5000,
            100,
            "algo",
            201,
        ),
        (
            tokens["leo2"],
            "partida3",
            2,
            3,
            4,
            8540,
            2,
            "algo",
            201,
        ),
    ]

    for (
        token,
        m_name,
        robot_id,
        min_p,
        max_p,
        games,
        rounds,
        password,
        expected_code,
    ) in test_matches:
        response = cl.post(
            "/matches/",
            headers={"token": token},
            json={
                "name": m_name,
                "robot_id": robot_id,
                "max_players": max_p,
                "min_players": min_p,
                "rounds": rounds,
                "games": games,
                "password": password,
            },
        )

        assert response.status_code == expected_code

    test_get_matches = [
        (
            tokens["bruno2"],
            "partida0",
            1,
            {"username": "bruno2", "avatar_url": None},
            2,
            4,
            10000,
            200,
            False,
            [{"name": "Marvin", "avatar_url": None, "username": "bruno2"}],
        ),
        (
            tokens["leo2"],
            "partida3",
            4,
            {"username": "leo2", "avatar_url": None},
            3,
            4,
            8540,
            2,
            False,
            [{"name": "R giskard", "avatar_url": None, "username": "leo2"}],
        ),
    ]

    # TODO add test for when get should return []
    response = cl.get(
        "/matches/?match_type=created", headers={"token": tokens["alvaro2"]}
    )

    assert response.status_code == 200
    assert not response.json()

    for i, (
        token,
        name,
        id,
        host,
        max_p,
        min_p,
        games,
        rounds,
        is_private,
        robots,
    ) in enumerate(test_get_matches):
        response = cl.get("/matches/?match_type=created", headers={"token": token})

        assert response.status_code == 200
        assert response.json()[i] == {
            "name": name,
            "id": id,
            "host": host,
            "max_players": min_p,
            "min_players": max_p,
            "games": games,
            "rounds": rounds,
            "is_private": is_private,
            "robots": robots,
        }


def test_join_nonexistant_match():
    user = register_random_users(1)[0]
    robot = create_random_robots(user["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": ""}
    tok_header = {"token": user["token"]}

    response = cl.put("/matches/1/join/", headers=tok_header, json=json_form)
    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Match not found"


def test_join_match_nonexistant_robot():
    user = register_random_users(1)[0]
    match = create_random_matches(user["token"], 1)[0]

    json_form = {"robot_id": 100000000, "password": match["password"]}
    tok_header = {"token": user["token"]}

    response = cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Robot not found"


def test_join_match_unowned_robot():
    users = register_random_users(2)
    robot = create_random_robots(users[0]["token"], 1)[0]
    match = create_random_matches(users[0]["token"], 1)[0]

    # robot id from first user, token from second
    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "Robot does not belong to user"


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

    response = cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "Match has already started"


def test_join_full_match():
    users = register_random_users(5)

    robots = []
    for user in users:
        robots.append(create_random_robots(user["token"], 1)[0])

    match = create_random_matches(users[0]["token"], 1)[0]

    for i, user in enumerate(users[1:-1], start=1):
        json_form = {"robot_id": robots[i]["id"], "password": match["password"]}
        tok_header = {"token": user["token"]}

        response = cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
        assert response.status_code == 201

    json_form = {"robot_id": robots[4]["id"], "password": match["password"]}
    tok_header = {"token": users[4]["token"]}

    response = cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "Match is full"


def test_join_match_invalid_password():
    users = register_random_users(2)
    match = create_random_matches(users[0]["token"], 1)[0]

    robot = create_random_robots(users[1]["token"], 1)[0]

    json_form = {"robot_id": robot["id"], "password": '1' + match["password"]}
    tok_header = {"token": users[1]["token"]}

    response = cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "Match password is incorrect"
