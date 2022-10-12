from core.models import *
from pony.orm import *

@db_session
def test_create():
    user = User(
        name="leo2",
        e_mail="leo2@gmail.com",
        password="123"
        )
    commit()
    assert(User.exists(name="leo2"))

