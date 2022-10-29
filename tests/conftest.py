import pytest

from app.models.database import db


@pytest.fixture(autouse=True)
def setup_test():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    yield
