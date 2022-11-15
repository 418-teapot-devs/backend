import pytest
from pony.orm import db_session

import app.views.users
from app.models import User, db


@pytest.fixture(autouse=True)
def verify_bypass(monkeypatch):
    def verify(email, _):
        with db_session:
            user = User.get(email=email)
            user.is_verified = True

    monkeypatch.setattr(app.views.users, "send_verification_token", verify)


@pytest.fixture(autouse=True)
def setup_test():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    yield
