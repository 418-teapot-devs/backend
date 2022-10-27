from pony.orm import db_session

from app.models import Robot, User, db


@db_session
def test_model():
    user1 = User(name="leo", email="leo@gemail.com", password="123")

    user2 = User(name="alvaro", email="alvaro@mi.unc.edu.ar", password="12334138924")

    user3 = User(name="anna", email="anna@mi.unc.edu.ar", password="1234331234")

    Robot(
        name="robot1",
        owner=user1,
    )

    Robot(
        name="robot2",
        owner=user2,
    )

    Robot(
        name="robot3",
        owner=user3,
    )

    assert (
        Robot.exists(name="robot1")
        and Robot.exists(name="robot2")
        and Robot.exists(name="robot3")
    )

    assert Robot.get(owner="leo", name="robot1").owner is User["leo"]

    db.rollback()
