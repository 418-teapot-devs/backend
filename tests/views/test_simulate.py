from urllib.parse import quote_plus

from fastapi.testclient import TestClient

from app.main import app
from app.util.assets import ASSETS_DIR

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])


def test_invalid_simulation():
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
    ]

    tokens = []
    for u in users:
        response = cl.post(f"/users/{json_to_queryparams(u)}")
        assert response.status_code == 201

        login_data = {"username": u["username"], "password": u["password"]}
        response = cl.post("/users/login/", json=login_data)
        assert response.status_code == 200

        data = response.json()
        tokens.append(data["token"])

    test_robots = [
        ("cesco", open(f"{ASSETS_DIR}/defaults/code/test_id_bot.py"), 201),
        ("lueme", open(f"{ASSETS_DIR}/defaults/code/test_loop_bot.py"), 201),
    ]

    for robot_name, code, expected_code in test_robots:
        files = []
        files.append(("code", code))

        response = cl.post(
            f"/robots/?name={robot_name}", headers={"token": tokens[0]}, files=files
        )
        assert response.status_code == expected_code

    response = cl.get("/robots/", headers={"token": tokens[0]})

    [cesco, lueme] = list(
        filter(
            lambda d: d["name"] == "cesco" or d["name"] == "lueme",
            list(response.json()),
        )
    )
    assert cesco["name"] == "cesco" and lueme["name"] == "lueme"

    simulations = [
        (500, [lueme["robot_id"]] * 5),
        (50000, [lueme["robot_id"], cesco["robot_id"]]),
    ]
    for s in simulations:
        response = cl.post(
            "/simulate/",
            headers={"token": tokens[0]},
            json={"rounds": s[0], "robots": s[1]},
        )
        assert response.status_code == 422

    simulations = [
        (500, [lueme["robot_id"]], 403),
        (50, [4638], 404),
    ]
    for rounds, robots, expected_code in simulations:
        response = cl.post(
            "/simulate/",
            headers={"token": tokens[1]},
            json={"rounds": rounds, "robots": robots},
        )
        assert response.status_code == expected_code


def test_run_simulation():
    user = {
        "username": "annaaimeri",
        "password": "AlpacaTactica158",
        "email": "annaaimeri@gemail.com",
    }

    response = cl.post(f"/users/{json_to_queryparams(user)}")
    assert response.status_code == 201

    login_data = {"username": user["username"], "password": user["password"]}
    response = cl.post("/users/login/", json=login_data)
    assert response.status_code == 200

    data = response.json()
    token = data["token"]

    test_robots = [
        ("cesco", open(f"{ASSETS_DIR}/defaults/code/test_id_bot.py"), 201),
        ("lueme", open(f"{ASSETS_DIR}/defaults/code/test_loop_bot.py"), 201),
    ]

    for robot_name, code, expected_code in test_robots:
        files = []
        files.append(("code", code))

        response = cl.post(
            f"/robots/?name={robot_name}", headers={"token": token}, files=files
        )
        assert response.status_code == expected_code

    response = cl.get("/robots/", headers={"token": token})
    [cesco, lueme] = list(
        filter(
            lambda d: d["name"] == "cesco" or d["name"] == "lueme",
            list(response.json()),
        )
    )
    assert cesco["name"] == "cesco" and lueme["name"] == "lueme"

    simulations = [
        ("666", [lueme]),
        ("500", [cesco]),
        ("345", [lueme, lueme, cesco]),
    ]
    for s in simulations:
        response = cl.post(
            "/simulate/",
            headers={"token": token},
            json={"rounds": s[0], "robots": list(map(lambda x: x["robot_id"], s[1]))},
        )
        assert response.status_code == 200
        assert len(response.json()["rounds"]) == int(s[0]) + 1
        response_robots = response.json()["robots"]
        assert response_robots == {
            str(i): {
                "name": r["name"],
                "avatar_url": None,
                "username": "annaaimeri",
            }
            for i, r in enumerate(s[1])
        }
