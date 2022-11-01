from pony.orm import db_session

from app.models import Robot, User, Match, RobotMatchResult, db


@db_session
def test_result_model():

    bruno = User(name="bruno", email="bruno@gmail.com", password="Burrito21")

    cesco = User(name="cesco", email="cesco@mi.unc.edu.ar", password="Burrito21")

    lueme = User(name="lueme", email="lueme@mi.unc.edu.ar", password="Burrito21")

    marvin = Robot(
        name="marvin",
        owner=bruno,
    )

    giskard = Robot(
        name="giskard",
        owner=cesco,
    )

    daneel = Robot(
        name="daneel",
        owner=lueme,
    )

    Match(
        name="partida1",
        host=bruno,
        plays={marvin, giskard, daneel},
        state="lobby",
        robot_count=3,
        max_players=4,
        min_players=2,
    )
    assert Match.exists(name="partida1")

    result_1 = RobotMatchResult(robot_id=1, match_id=1, position=2, death_count= 3, condition="Lost" )

    result_2 = RobotMatchResult(robot_id=2, match_id=1, position=1, death_count= 0, condition="Won" )

    assert RobotMatchResult.exists(robot_id=1,match_id=1) and RobotMatchResult.exists(robot_id=2,match_id=1)

    db.rollback()
