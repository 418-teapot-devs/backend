from pony.orm import db_session

from core.models import Robot, User, db


@db_session
def test_model():
    user1 = User(name="leo", e_mail="leo@gmail.com", password="123")

    user2 = User(name="alvaro", e_mail="alvaro@mi.unc.edu.ar", password="12334138924")

    user3 = User(name="anna", e_mail="anna@mi.unc.edu.ar", password="1234331234")

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

    assert Robot[User["leo"], "robot1"].owner is User["leo"]

    db.rollback()
