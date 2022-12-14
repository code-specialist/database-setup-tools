import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.scoping import ScopedSession

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup
from tests.sample_model import model_metadata, User


@pytest.mark.parametrize('database_uri', ["sqlite:///test.db"])
class TestDatabaseIntegration:

    @pytest.fixture
    def database_setup(self, database_uri: str) -> DatabaseSetup:
        setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        yield setup
        setup.drop_database()

    @pytest.fixture
    def database_session(self, database_uri: str) -> ScopedSession:
        """ Get a database session """
        session_manager = SessionManager(database_uri)
        return next(session_manager.get_session())

    def test_create_database_and_tables(self, database_setup: DatabaseSetup, database_session: ScopedSession):
        """ Test that the tables are created correctly """
        database_setup.create_database()

        # noinspection SqlInjection,SqlDialectInspection
        test_query = database_session.execute(f'SELECT * FROM {User.__tablename__}')

        assert test_query.cursor.description[0][0] == 'id'
        assert test_query.cursor.description[1][0] == 'name'

    def test_drop_database(self, database_setup: DatabaseSetup, database_session: ScopedSession):
        """ Test that the database is dropped correctly """
        database_setup.create_database()
        assert database_setup.drop_database() is True

        with pytest.raises(OperationalError):
            # noinspection SqlDialectInspection
            database_session.execute(f'SELECT * FROM {User.__tablename__}')

        assert database_setup.drop_database() is False
