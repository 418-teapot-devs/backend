from pony.orm import db_session

from app.models import Match, Robot, User, db


@db_session
def test_model():
    leo = User(name="leo", email="leo@gmail.com", password="patria o paper")

    alvaro = User(
        name="alvaro", email="alvaro@mi.unc.edu.ar", password="aguante el ceimaf"
    )

    anna = User(name="anna", email="anna@mi.unc.edu.ar", password="1234331234")

    sylveon = Robot(
        name="sylveon",
        owner=alvaro,
    )

    caterpie = Robot(
        name="caterpie",
        owner=leo,
    )

    oricorio = Robot(
        name="oricorio",
        owner=anna,
    )

    Match(
        name="bg!",
        host=alvaro,
        plays={sylveon, caterpie, oricorio},
        state="lobyy",
        robot_count=3,
        max_players=4,
        min_players=2,
    )
    assert Match.exists(name="bg!")

    assert (
        (Robot.get(owner="leo", name="caterpie") in Match[1].plays)
        and (Robot.get(owner="alvaro", name="sylveon") in Match[1].plays)
        and (Robot.get(owner="anna", name="oricorio") in Match[1].plays)
    )

    assert Match[1].host is User["alvaro"]

    db.rollback()
