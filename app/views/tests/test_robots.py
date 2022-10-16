from datetime import timedelta
from urllib.parse import quote_plus

from fastapi.testclient import TestClient

from main import app
from views.users import create_access_token

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def test_create_robot():
    user = {
        "username": "annaaimeri",
        "password": "AlpacaTactica158",
        "e_mail": "annaaimeri@gmail.com",
    }

    response = cl.post(
        f"/users/{json_to_queryparams(user)}"
    )
    assert response.status_code == 200

    data = response.json()
    token = data["token"]
    fake_token = create_access_token({"sub": "login", "username": "pepito"}, timedelta(hours=1.0))

    test_robots = [
        ("cesco", token, "identity.py", None, 200),
        ("lueme", token, "identity.py", "identity_avatar.png", 200),
        ("fnazar", fake_token, "identity.py", None, 404),
        # ("hola", "hola", ["robot", "identity.py"], 200), TODO handle more jwt errors (fake token)
    ]

    for robot_name, token, code, avatar, expected_code in test_robots:
        files = []
        if code:
            files.append(("robot", code))

        if avatar:
            files.append(("avatar", avatar))

        response = cl.post(
            f"/robots/?name={robot_name}",
            headers={"token": token},
            files=files
        )
        assert response.status_code == expected_code
