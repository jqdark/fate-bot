import pytest

from fate.database.database import Database


class TestDatabase:

    @pytest.fixture
    def db(self):

        # In-memory database
        db = Database("sqlite://")
        db.create_tables()

        return db


    def test_fetch_user(self, db):
        
        assert db.fetch_user(100, create_missing=False) is None
        assert db.fetch_user(100) is not None

        user = db.fetch_user(100, create_missing=False)
        assert user is not None
        assert user.discord_id == 100
        assert user.profile is None

        # Existing user does not change behaviour for new user
        assert db.fetch_user(137, create_missing=False) is None
        assert db.fetch_user(137) is not None
        assert db.fetch_user(137, create_missing=False) is not None
