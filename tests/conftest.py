import pytest
from lightsoff_api import app, db


@pytest.fixture(scope="function")
def db_fixture():
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def client(db_fixture):
    return app.test_client()
