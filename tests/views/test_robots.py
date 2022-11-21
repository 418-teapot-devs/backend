from datetime import timedelta
from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from pony.orm import db_session

from app.main import app
from app.models import Robot
from app.views.users import create_access_token
from tests.testutil import (
    create_random_matches,
    create_random_robots,
    register_random_users,
)

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def test_create_robot():
    [user] = register_random_users(1)
    token = user["token"]

    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )

    test_robots = [
        {"token": token, "name": "cesco", "code": True, "expected_code": 201},
        {"token": token, "name": "cesco", "code": True, "expected_code": 409},
        {"token": token, "name": "lueme", "code": False, "expected_code": 422},
        {
            "token": fake_token,
            "name": "locke",
            "code": True,
            "expected_code": 404,
        },
    ]

    robot_code = open("tests/assets/defaults/code/test_id_bot.py")

    for m in test_robots:
        files = []
        if m["code"]:
            robot_code.seek(0)
            files.append(("code", robot_code))

        response = cl.post(
            f'/robots/?name={m["name"]}', headers={"token": m["token"]}, files=files
        )
        assert response.status_code == m["expected_code"]

        if m["expected_code"] == 201:
            with db_session:
                assert Robot.exists(name=m["name"])


def test_check_invalid_syntax():
    [user] = register_random_users(1)
    token = user["token"]
    response = cl.post(
        f"/robots/?name=nofunca", headers={"token": token}, files=[("code", "robot._)")]
    )
    assert response.status_code == 418
    assert response.json()["detail"] == "Syntax error"


base_src = """class Bot(Robot):
    def initialize(self):
        pass
    def respond(self):
        pass
"""


def test_check_imports():
    [user] = register_random_users(1)
    token = user["token"]
    srcs = [
        "import os\n" + base_src,
        "import importlib as i\n" + base_src,
        "from ..app.game import entities",
        "from os import chroot\n" + base_src,
    ]

    for src in srcs:
        response = cl.post(
            f"/robots/?name=bot", headers={"token": token}, files=[("code", src)]
        )
        assert response.status_code == 418
        assert (
            response.json()["detail"] == "Forbidden functions or imports found in code"
        )


def test_check_builtins():
    [user] = register_random_users(1)
    token = user["token"]
    srcs = [
        '__import__("os")\n' + base_src,
        "v = datetime.__vars__\n" + base_src,
        'import numpy\ngetattr(numpy, "__builtins__")\n' + base_src,
        'exec("import os\\ni = os.__builtins__.__import__")\n' + base_src,
        'open("randomfile", "w").write("random stuff")\n' + base_src,
    ]

    for src in srcs:
        response = cl.post(
            f"/robots/?name=bot", headers={"token": token}, files=[("code", src)]
        )
        assert response.status_code == 418
        assert (
            response.json()["detail"] == "Forbidden functions or imports found in code"
        )


def test_check_methods():
    [user] = register_random_users(1)
    token = user["token"]
    src1 = "\n".join(base_src.splitlines()[:-2])  # class without a method
    src2 = base_src + "    def get_damage(self):\n        self._dmg = 0\n"

    response = cl.post(
        f"/robots/?name=bot", headers={"token": token}, files=[("code", src1)]
    )
    assert response.status_code == 418
    assert response.json()["detail"] == "Methods initialize or respond not implemented"

    response = cl.post(
        f"/robots/?name=bot", headers={"token": token}, files=[("code", src2)]
    )
    assert response.status_code == 418
    assert response.json()["detail"] == "Invalid name for method or attribute of robot"


def test_check_classes():
    [user] = register_random_users(1)
    token = user["token"]
    src1 = base_src + base_src
    src2 = base_src + "class A(Robot, Exception):\n    def initialize(self): pass\n"

    response = cl.post(
        f"/robots/?name=bot", headers={"token": token}, files=[("code", src1)]
    )
    assert response.status_code == 418
    assert (
        response.json()["detail"]
        == "Code must define exactly one class that inherits from Robot"
    )

    response = cl.post(
        f"/robots/?name=bot", headers={"token": token}, files=[("code", src2)]
    )
    assert response.status_code == 418
    assert (
        response.json()["detail"]
        == "Code must define exactly one class that inherits from Robot"
    )


def test_get_robots():
    users = register_random_users(2)
    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )

    response = cl.get("/robots/", headers={"token": fake_token})
    assert response.status_code == 404

    robots_u1 = create_random_robots(users[0]["token"], 2)
    robots_u2 = create_random_robots(users[1]["token"], 1)

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
            },
            {
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
        response = cl.get("/robots/", headers={"token": users[i]["token"]})
        assert response.json() == r


def test_robot_results():
    host, *players = register_random_users(4)

    create_random_robots(host["token"], 33)
    match = create_random_matches(host["token"], 1)[0]

    for player in players:
        player["robot"] = create_random_robots(player["token"], 1)[0]

        join_form = {"robot_id": player["robot"]["id"], "password": match["password"]}
        token_header = {"token": player["token"]}

        response = cl.put(
            f"/matches/{match['id']}/join/", headers=token_header, json=join_form
        )
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


def test_get_robot_details():
    [user1, user2] = register_random_users(2)
    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )

    response = cl.get("/robots/1/", headers={"token": fake_token})
    assert response.status_code == 404

    response = cl.get("/robots/10000/", headers={"token": user1["token"]})
    assert response.status_code == 404

    response = cl.get("/robots/1/", headers={"token": user2["token"]})
    assert response.status_code == 403

    response = cl.get("/robots/1/", headers={"token": user1["token"]})
    assert response.status_code == 200
    assert len(response.json()["code"]) > 0


def test_update_robot_code():
    [user1, user2] = register_random_users(2)
    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )

    with open("tests/assets/defaults/code/test_id_bot.py") as f:
        new_code = f.read()

    response = cl.put(
        "/robots/1/", headers={"token": fake_token}, json={"code": new_code}
    )
    assert response.status_code == 404

    response = cl.put(
        "/robots/10/", headers={"token": user1["token"]}, json={"code": new_code}
    )
    assert response.status_code == 404

    response = cl.put(
        "/robots/1/", headers={"token": user2["token"]}, json={"code": new_code}
    )
    assert response.status_code == 403

    response = cl.put(
        "/robots/1/", headers={"token": user1["token"]}, json={"code": "int main(void)"}
    )
    assert response.status_code == 418

    response = cl.put(
        "/robots/1/", headers={"token": user1["token"]}, json={"code": new_code}
    )
    assert response.status_code == 200

    response = cl.get("/robots/1/", headers={"token": user1["token"]})
    assert response.status_code == 200
    assert response.json()["code"] == new_code
