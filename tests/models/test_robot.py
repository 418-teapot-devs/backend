from pony.orm import db_session

from app.models import Robot, User, db


@db_session
def test_robot_model():
    bruno = User(name="bruno", email="bruno@gmail.com", password="123")

    cesco = User(name="cesco", email="cesco@mi.unc.edu.ar", password="12334138924")

    lueme = User(name="lueme", email="lueme@mi.unc.edu.ar", password="1234331234")

    Robot(
        name="amoonguss",
        owner=bruno,
    )

    Robot(
        name="zubat",
        owner=cesco,
    )

    Robot(
        name="ledian",
        owner=lueme,
    )

    assert Robot.exists(name="amoonguss")
    assert Robot.exists(name="zubat")
    assert Robot.exists(name="ledian")

    assert Robot.get(owner="bruno", name="amoonguss").owner is bruno
    assert Robot.get(owner="cesco", name="zubat").owner is cesco
    assert Robot.get(owner="lueme", name="ledian").owner is lueme

    db.rollback()
