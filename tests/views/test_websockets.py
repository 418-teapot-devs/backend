from fastapi.testclient import TestClient
import pytest
from fastapi import websockets
from app.main import app
from tests.testutil import register_random_users, create_random_matches, create_random_robots

cl = TestClient(app)

def test_websocket_invalid_connect():
    with pytest.raises(websockets.WebSocketDisconnect):
        with cl.websocket_connect("/matches/5/ws"):
            assert False


def test_websocket_data_on_connect():
    [user] = register_random_users(1)
    [match] = create_random_matches(user["token"], 1)

    with cl.websocket_connect(f"/matches/{match['id']}/ws") as ws:
        response = ws.receive_json()

    assert response["id"] == int(match["id"])
    assert response["host"] == {"username": user["username"], "avatar_url": None}
    assert response["state"] == "Lobby"
    assert response["results"] is None


def test_websocket_update_data():
    users = register_random_users(2)
    [robot] = create_random_robots(users[1]["token"], 1)
    [match] = create_random_matches(users[0]["token"], 1)

    json_form = {"robot_id": robot["id"], "password": match["password"]}
    tok_header = {"token": users[1]["token"]}

    with cl.websocket_connect(f"/matches/{match['id']}/ws") as ws:
        response = ws.receive_json()
        assert len(response["robots"]) == 1

        cl.put(f"/matches/{match['id']}/join/", headers=tok_header, json=json_form)
        response = ws.receive_json()
        assert len(response["robots"]) == 2

        response = cl.put(f"/matches/{match['id']}/leave/", headers=tok_header)

        response = ws.receive_json()
        assert len(response["robots"]) == 1


def test_websocket_change_state():
    users = register_random_users(2)
    robots = sum((create_random_robots(users[i]["token"], 1) for i in range(2)), [])

    create_json = {
                "name": "match",
                "robot_id": robots[0]["id"],
                "max_players": 2,
                "min_players": 2,
                "rounds": 5,
                "games": 1,
                "password": "123",
            }
    join_json = {"robot_id": robots[1]["id"], "password": "123"}
    tok_headers = [{"token": users[i]["token"]} for i in range(2)]

    cl.post(f"/matches/", headers=tok_headers[0], json=create_json)
    cl.put(f"/matches/1/join/", headers=tok_headers[1], json=join_json)

    with cl.websocket_connect(f"/matches/1/ws") as ws:
        response = ws.receive_json()
        assert response["state"] == "Lobby"
        assert response["results"] is None

        cl.put(f"/matches/1/start/", headers=tok_headers[0])

        response = ws.receive_json()
        assert response["state"] == "InGame"
        assert response["results"] is None

        response = ws.receive_json()
        assert response["state"] == "Finished"
        assert response["results"] is not None


def test_websocket_finished_connect():
    users = register_random_users(2)
    [robot] = create_random_robots(users[1]["token"], 1)
    match = create_random_matches(users[0]["token"], 6)[-1]
    tok_headers = [{"token": users[i]["token"]} for i in range(2)]

    json_form = {"robot_id": robot["id"], "password": match["password"]}

    cl.put(f"/matches/{match['id']}/join/", headers=tok_headers[1], json=json_form)

    cl.put(f"/matches/{match['id']}/start/", headers=tok_headers[0])

    with cl.websocket_connect(f"/matches/{match['id']}/ws") as ws:
        response = ws.receive_json()

        assert response["state"] == "Finished"
        assert response["results"] is not None
