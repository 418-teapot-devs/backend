
from core.models import *
from pony.orm import *

@db_session
def test_model():
    user1 = User(
        name="leo1",
        e_mail="leo1@gmail.com",
        password="123"
        )

    user2 = User(
        name="alvaro1",
        e_mail="alvaro1@mi.unc.edu.ar",
        password="12334138924"
        )

    user3 = User(
        name="anna1",
        e_mail="anna1@mi.unc.edu.ar",
        password="1234331234"
        )

    robot1 = Robot(
        name="robot11",
        owner=user1,
        )

    robot2 = Robot(
        name="robot21",
        owner=user2,
        )

    robot3 = Robot(
        name="robot31",
        owner=user3,
        )

    assert(Robot.exists(name="robot11") and Robot.exists(name="robot21") and Robot.exists(name="robot31"))

    assert(Robot[User["leo1"],"robot11"].owner is User["leo1"])
#@db_session
#def test_owner():

