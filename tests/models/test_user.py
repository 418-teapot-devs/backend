from pony.orm import db_session

from app.models import User, db


@db_session
def test_create():
    User(name="leo", email="leo@gmail.com", password="123")

    user = User.get(name="leo")
    assert user is not None
    assert user.email == "leo@gmail.com"
    assert user.password == "123"

    db.rollback()
