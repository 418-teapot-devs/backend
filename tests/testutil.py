import random
import string
from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from pony.orm import commit, db_session

from app.main import app
from app.models.match import Match
from app.models.robot import Robot
from app.models.user import User
from app.util.auth import get_current_user

cl = TestClient(app)


def test_must_fail():
    assert False


def random_ascii_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def register_random_users(count):
    users = [
        {"username": None, "password": None, "email": None, "token": None}
        for _ in range(count)
    ]

    for i in range(count):
        username = f"{i}" + random_ascii_string(9)
        password = f"{i}Ab" + random_ascii_string(5)
        email = f"{i}@randomjunk.com"

        json_form = {"username": username, "password": password, "email": email}

        response = cl.post(f"/users/{json_to_queryparams(json_form)}")
        assert response.status_code == 201

        data = response.json()

        users[i]["username"] = username
        users[i]["password"] = password
        users[i]["email"] = email
        users[i]["token"] = data["token"]

    return users


def create_random_robots(token, count):
    robots = [{"id": None, "name": None} for _ in range(count)]
    robot_code = open("tests/assets/defaults/code/test_id_bot.py")

    for i in range(count):
        robotname = f"{i}" + random_ascii_string(9)

        tok_header = {"token": token}

        response = cl.post(
            f"/robots/?name={quote_plus(robotname)}",
            headers=tok_header,
            files=[("code", robot_code)],
        )
        assert response.status_code == 201

        response = cl.get("/robots/", headers=tok_header)
        assert response.status_code == 200

        robot = next(r for r in response.json() if r["name"] == robotname)

        robots[i]["id"] = f"{robot['robot_id']}"
        robots[i]["name"] = robotname

    robot_code.close()
    return robots


@db_session
def create_random_matches(token, count):
    username = get_current_user(token)
    user = User[username]

    robot = create_random_robots(token, 1)[0]
    robot = Robot[robot["id"]]

    matches = [{"id": None, "password": None} for _ in range(count)]
    for i in range(count):
        password = random_ascii_string(10)
        match = Match(
            name=random_ascii_string(10),
            host=user,
            plays={robot},
            state="Lobby",
            robot_count=1,
            max_players=4,
            min_players=2,
            password=password,
        )
        commit()

        matches[i]["id"] = f"{match.id}"
        matches[i]["password"] = password

    return matches
