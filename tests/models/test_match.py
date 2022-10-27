from pony.orm import db_session

from app.models import Match, Robot, User, db


@db_session
def test_model():
    user1 = User(name="leo", email="leo@gemail.com", password="123")

    user2 = User(
        name="alvaro", email="alvaro@mi.unc.edu.ar", password="aguante el ceimaf"
    )

    user3 = User(name="anna", email="anna@mi.unc.edu.ar", password="1234331234")

    robot1 = Robot(
        name="robot1",
        owner=user1,
    )

    robot2 = Robot(
        name="robot2",
        owner=user2,
    )

    robot3 = Robot(
        name="robot3",
        owner=user3,
    )

    Match(
        name="partida1",
        host=User["alvaro"],
        plays={robot1, robot2, robot3},
        state="lobyy",
        robot_count=3,
        max_players=4,
        min_players=2,
    )
    assert Match.exists(name="partida1")

    assert (
        (Robot.get(owner="leo", name="robot1") in Match[1].plays)
        and (Robot.get(owner="alvaro", name="robot2") in Match[1].plays)
        and (Robot.get(owner="anna", name="robot3") in Match[1].plays)
    )

    assert Match[1].host is User["alvaro"]

    db.rollback()
