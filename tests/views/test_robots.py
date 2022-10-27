from datetime import timedelta
from urllib.parse import quote_plus

from fastapi.testclient import TestClient

from app.main import app
from app.views.users import create_access_token

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def test_create_robot():
    user = {
        "username": "annaaimeri",
        "password": "AlpacaTactica158",
        "email": "annaaimeri@gemail.com",
    }

    response = cl.post(f"/users/{json_to_queryparams(user)}")
    assert response.status_code == 201

    data = response.json()
    token = data["token"]
    fake_token = create_access_token(
        {"sub": "login", "username": "pepito"}, timedelta(hours=1.0)
    )

    test_robots = [
        ("cesco", token, "identity.py", None, 201),
        ("lueme", token, "identity.py", "identity_avatar.png", 201),
        ("lueme", token, "identity.py", "identity_avatar.png", 409),
        ("oricolo", token, None, "identity_avatar.png", 422),
        ("fnazar", fake_token, "identity.py", None, 404),
        # ("hola", "hola", ["robot", "identity.py"], 200), TODO handle more jwt errors (fake token)
    ]

    for robot_name, token, code, avatar, expected_code in test_robots:
        files = []
        if code:
            files.append(("code", code))

        if avatar:
            files.append(("avatar", avatar))

        response = cl.post(
            f"/robots/?name={robot_name}", headers={"token": token}, files=files
        )
        assert response.status_code == expected_code


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

        if robot["avatar"]:
            assert f"{robot['id']}" in robot["avatar"]
        else:
            assert not robot["avatar"]
