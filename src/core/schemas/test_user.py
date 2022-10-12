from pony.orm import db_session

from core.models import User, db


@db_session
def test_create():
    User(name="leo", e_mail="leo@gmail.com", password="123")

    user = User.get(name="leo")
    assert user is not None
    assert user.e_mail == "leo@gmail.com"
    assert user.password == "123"

    db.rollback()
