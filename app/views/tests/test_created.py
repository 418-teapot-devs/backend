from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from jose import jwt
from pony.orm import db_session

from core.models import db, Robot, Match
from main import app
from views import JWT_ALGORITHM, JWT_SECRET_KEY

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])

def test_created_invalid_match():
    users = [
            {"username": "alvaro", "password": "MILC(man,i love ceimaf)123", "e_mail": "a@gmail.com"},
            {"username": "bruno", "password": "h0la soy del Monse", "e_mail": "b@gmail.com"},
            {"username": "leo", "password": "Burrito21", "e_mail": "l@gmail.com"},
    ]

    responses = []
    tokens = {}
    for u in users:
        response = cl.post(f"/users/{json_to_queryparams(u)}") 
        assert response.status_code == 200
        data = response.json()

        tokens[u["username"]] = data["token"]

    test_robots = [
            ("daneel R olivaw", tokens["leo"], "identity.py", None, 201),
            ("R giskard", tokens["leo"], "identity.py", None, 201),
            ("Marvin", tokens["bruno"], "identity.py", None, 201),
            ("deep thought", tokens["alvaro"], "identity.py", None, 201),
    ]


    for robot_name, token, code, avatar, expected_code in test_robots:
        files = []
        if code:
            files.append(("code", code))

        response = cl.post(f"/robots/?name={robot_name}", headers={"token": token}, files=files)

        assert response.status_code == expected_code

    test_matches = [
            ("fadsfasdfasdfasdfasdfa", "partida1", "Marvin", 2, 4, 10000, 200, "algo", "Lobby" , 3, 404),
            (tokens["bruno"], "partida1", "robo nao existe", 2, 4, 10000, 200, "algo", "Lobby" , 3, 404),
    ]

    for token, m_name, r_name, min_p, max_p, games, rounds, password, state, robot_id, expected_code in test_matches:

        response = cl.post(f"/matches/created", headers={"token": token},
                            json = {"name": m_name,"name_robot": r_name, "max_players": min_p,
                                "min_players": max_p, "rounds": rounds, "games": games,
                                "password": password,"state": state ,"robotId": robot_id})

        assert response.status_code == expected_code

def test_post_created():
    users = [
            {"username": "alvaro1", "password": "MILC(man,i love ceimaf)123", "e_mail": "a1@gmail.com"},
            {"username": "bruno1", "password": "h0la soy del Monse", "e_mail": "b1@gmail.com"},
            {"username": "leo1", "password": "Burrito21", "e_mail": "l1@gmail.com"}
    ]

    responses = []
    tokens = {}
    for u in users:
        response = cl.post(f"/users/{json_to_queryparams(u)}") 
        assert response.status_code == 200
        data = response.json()

        tokens[u["username"]] = data["token"]

    test_robots = [
            ("daneel R olivaw", tokens["leo1"], "identity.py", None, 201),
            ("R giskard", tokens["leo1"], "identity.py", None, 201),
            ("Marvin", tokens["bruno1"], "identity.py", None, 201),
            ("deep thought", tokens["alvaro1"], "identity.py", None, 201),
    ]


    for robot_name, token, code, avatar, expected_code in test_robots:
        files = []
        if code:
            files.append(("code", code))

        response = cl.post(f"/robots/?name={robot_name}", headers={"token": token}, files=files)

        assert response.status_code == expected_code

    test_matches = [
            (tokens["bruno1"], "partida1", "Marvin", 2, 4, 10000, 200, "algo", "Lobby" , 3, 201),
             (tokens["leo1"], "partida2", "daneel R olivaw", 2, 4, 5000, 100, "algo", "Lobby", 1, 201),
             (tokens["leo1"], "partida3", "R giskard", 3, 4, 8540, 2, "algo", "Lobby", 2, 201)
    ]

    for token, m_name, r_name, min_p, max_p, games, rounds, password, state, robot_id, expected_code in test_matches:

        response = cl.post(f"/matches/created", headers={"token": token},
                            json = {"name": m_name,"name_robot": r_name, "max_players": max_p,
                                "min_players": min_p, "rounds": rounds, "games": games,
                                "password": password,"state": state ,"robotId": robot_id})

        assert response.status_code == expected_code

def test_get_created():
    users = [
            {"username": "alvaro2", "password": "MILC(man,i love ceimaf)123", "e_mail": "a2@gmail.com"},
            {"username": "bruno2", "password": "h0la soy del Monse", "e_mail": "b2@gmail.com"},
            {"username": "leo2", "password": "Burrito21", "e_mail": "l2@gmail.com"},
    ]

    tokens = {}
    for u in users:
        response = cl.post(f"/users/{json_to_queryparams(u)}") 
        assert response.status_code == 200
        data = response.json()

        tokens[u["username"]] = data["token"]

    test_robots = [
            ("daneel R olivaw", tokens["leo2"], "identity.py", None, 201),
            ("R giskard", tokens["leo2"], "identity.py", None, 201),
            ("Marvin", tokens["bruno2"], "identity.py", None, 201),
            ("deep thought", tokens["alvaro2"], "identity.py", None, 201),
    ]


    for robot_name, token, code, avatar, expected_code in test_robots:
        files = []
        if code:
            files.append(("code", code))

        response = cl.post(f"/robots/?name={robot_name}", headers={"token": token}, files=files)

        assert response.status_code == expected_code

    test_matches = [
            (tokens["bruno2"], "partida0", "Marvin", 2, 4, 10000, 200, "algo", "Lobby",3, 201),
            (tokens["bruno2"], "partida1", "Marvin", 2, 4, 10000, 200, "algo", "InGame" , 3, 201),
            (tokens["leo2"], "partida2", "daneel R olivaw", 2, 4, 5000, 100, "algo", "Finished", 1, 201),
            (tokens["leo2"], "partida3", "R giskard", 3, 4, 8540, 2, "algo", "Lobby", 2, 201)
    ]

    for token, m_name, r_name, min_p, max_p, games, rounds, password, state, robot_id, expected_code in test_matches:

        response = cl.post(f"/matches/created", headers={"token": token},
                            json = {"name": m_name,"name_robot": r_name, "max_players": max_p,
                                "min_players": min_p, "rounds": rounds, "games": games,
                                "password": password,"state": state ,"robotId": robot_id})

        assert response.status_code == expected_code

    test_get_matches = [
            (tokens["bruno2"], "partida0", 2,4,10000,200,False,[{"name": "Marvin","avatar_url": None, "username": "bruno2"} ] ),
            (tokens["leo2"], "partida3", 3,4,8540,2,False,[{"name": "R giskard","avatar_url": None, "username": "leo2"} ] )
            ]
            #TODO add test for when get should return []

    for token, name , max_p, min_p, games, rounds, is_private, robots in test_get_matches:
        response = cl.get(f"/matches/created", headers={"token": token})
        assert response.json() == [{"name": name,"max_players": min_p,
                                    "min_players": max_p, "games": games, "rounds": rounds,
                                    "is_private": is_private, "robots" : robots}]


