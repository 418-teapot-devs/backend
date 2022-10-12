from core.models import *
from pony.orm import *

@db_session
def test_model():
    user1 = User(
        name="leo",
        e_mail="leo@gmail.com",
        password="123"
        )

    user2 = User(
        name="alvaro",
        e_mail="alvaro@mi.unc.edu.ar",
        password="aguante el ceimaf"
        )

    user3 = User(
        name="anna",
        e_mail="anna@mi.unc.edu.ar",
        password="1234331234"
        )

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


    match1 = Match(
            name="partida1",
            host=user.User['alvaro'],
            plays={robot1,robot2,robot3},
            state="lobyy",
            robot_count=3
            )
    assert(Match.exists(name="partida1"))


@db_session
def test_players():
    assert((Robot[User['leo'],'robot1'] in Match[1].plays) and (Robot[User['alvaro'],'robot2'] in Match[1].plays) and (Robot[User['alvaro'],'robot2'] in Match[1].plays))


@db_session
def test_host():
   assert( Match[1].host is User['alvaro'])
