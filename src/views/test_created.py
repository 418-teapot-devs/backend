from urllib.parse import quote_plus

from fastapi.testclient import TestClient
from jose import jwt
from pony.orm import db_session

from core.models import db, Robot, Match
from ..main import app
from ..views import JWT_ALGORITHM, JWT_SECRET_KEY

cl = TestClient(app)


def json_to_queryparams(json: dict):
    return "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in json.items()])

def test_created_invalid_match():

    # Upload users
    user1 = {
        "username": "alvaro",
        "password": "MILC(man, i love ceimaf)123",
        "e_mail": "a@gmail.com"
    }

    user2 = {
        "username": "anna",
        "password": "Burrito21",
        "e_mail": "an@gmail.com"
    }

    user3 = {
        "username": "bruno",
        "password": "Soy del m0nse",
        "e_mail": "b@gmail.com"
    }

    response1 = cl.post(f"/users/{json_to_queryparams(user1)}")
    response2 = cl.post(f"/users/{json_to_queryparams(user2)}")
    response3 = cl.post(f"/users/{json_to_queryparams(user3)}")
    assert response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200

    data1 = response1.json()
    toke1 = data1["token"]

    data2 = response2.json()
    toke2 = data2["token"]

    data3 = response3.json()
    toke3 = data3["token"]

    #upload robot data to database

    robot1 = {
            "name": "robot1",
            "code": "lalal"
        }
    
    robot2 = {
            "name": "robot1",
            "code": "lalal"
        }

    robot3 = {
            "name": "robot3",
            "code": "lalal"
            }

    robot1 = cl.post(f"/robots{json_to_queryparams(user1)}")
    with db_session:

        r1 = Robot(name="robot1",owner=User.get(name="leo"))
        r2 = Robot(name="robot2",owner=User.get(name="alvaro"))
        r3 = Robot(name="robot3",owner=User.get(name="anna"))

        drop_all_tables()

