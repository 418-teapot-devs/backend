from urllib.parse import quote_plus

from fastapi.testclient import TestClient

from app.main import app

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


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
            "Marvin",
            2,
            4,
            10000,
            200,
            "algo",
            "Lobby",
            3,
            404,
        ),
        (
            tokens["bruno"],
            "partida1",
            "robo nao existe",
            2,
            4,
            10000,
            200,
            "algo",
            "Lobby",
            3,
            404,
        ),
    ]

    for (
        token,
        m_name,
        r_name,
        min_p,
        max_p,
        games,
        rounds,
        password,
        state,
        robot_id,
        expected_code,
    ) in test_matches:
        response = cl.post(
            "/matches/created",
            headers={"token": token},
            json={
                "name": m_name,
                "name_robot": r_name,
                "max_players": min_p,
                "min_players": max_p,
                "rounds": rounds,
                "games": games,
                "password": password,
                "state": state,
                "robotId": robot_id,
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
            "Moltres",
            2,
            4,
            10000,
            200,
            "algo",
            "Lobby",
            3,
            201,
        ),
        (
            tokens["leo1"],
            "partida2",
            "Raichu",
            2,
            4,
            5000,
            100,
            "algo",
            "Lobby",
            1,
            201,
        ),
        (tokens["leo1"], "partida3", "Zubat", 3, 4, 8540, 2, "algo", "Lobby", 2, 201),
    ]

    for (
        token,
        m_name,
        r_name,
        min_p,
        max_p,
        games,
        rounds,
        password,
        state,
        robot_id,
        expected_code,
    ) in test_matches:
        response = cl.post(
            "/matches/created",
            headers={"token": token},
            json={
                "name": m_name,
                "name_robot": r_name,
                "max_players": max_p,
                "min_players": min_p,
                "rounds": rounds,
                "games": games,
                "password": password,
                "state": state,
                "robotId": robot_id,
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
            "Marvin",
            2,
            4,
            10000,
            200,
            "algo",
            "Lobby",
            3,
            201,
        ),
        (
            tokens["bruno2"],
            "partida1",
            "Marvin",
            2,
            4,
            10000,
            200,
            "algo",
            "InGame",
            3,
            201,
        ),
        (
            tokens["leo2"],
            "partida2",
            "daneel R olivaw",
            2,
            4,
            5000,
            100,
            "algo",
            "Finished",
            1,
            201,
        ),
        (
            tokens["leo2"],
            "partida3",
            "R giskard",
            3,
            4,
            8540,
            2,
            "algo",
            "Lobby",
            2,
            201,
        ),
    ]

    for (
        token,
        m_name,
        r_name,
        min_p,
        max_p,
        games,
        rounds,
        password,
        state,
        robot_id,
        expected_code,
    ) in test_matches:
        response = cl.post(
            "/matches/created",
            headers={"token": token},
            json={
                "name": m_name,
                "name_robot": r_name,
                "max_players": max_p,
                "min_players": min_p,
                "rounds": rounds,
                "games": games,
                "password": password,
                "state": state,
                "robotId": robot_id,
            },
        )

        assert response.status_code == expected_code

    test_get_matches = [
        (
            tokens["bruno2"],
            "partida0",
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
            3,
            4,
            8540,
            2,
            False,
            [{"name": "R giskard", "avatar_url": None, "username": "leo2"}],
        ),
    ]

    # TODO add test for when get should return []
    response = cl.get("/matches/created", headers={"token": tokens["alvaro2"]})

    assert response.status_code == 200
    assert not response.json()

    for i, (
        token,
        name,
        max_p,
        min_p,
        games,
        rounds,
        is_private,
        robots,
    ) in enumerate(test_get_matches):
        response = cl.get("/matches/created", headers={"token": token})

        assert response.status_code == 200
        assert response.json()[i] == {
            "name": name,
            "max_players": min_p,
            "min_players": max_p,
            "games": games,
            "rounds": rounds,
            "is_private": is_private,
            "robots": robots,
        }
