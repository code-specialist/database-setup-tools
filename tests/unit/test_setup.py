import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.scoping import ScopedSession

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup
from tests.unit.sample_model import model_metadata


def get_database_session(database_uri: str) -> ScopedSession:
    """ Get a database session """
    session_manager = SessionManager(database_uri)
    return next(session_manager.get_session())


class TestSetup:

    @staticmethod
    def test_database_setup_is_singleton(database_uri='sqlite://'):
        """ Test that the DatabaseSetup is a singleton """
        database_setup_1 = DatabaseSetup(model_metadata, database_uri)
        database_setup_2 = DatabaseSetup(model_metadata, database_uri)
        database_setup_3 = DatabaseSetup(model_metadata, database_uri)
        assert database_setup_1 is database_setup_2 is database_setup_3

    @staticmethod
    def test_database_uri(database_uri='sqlite://'):
        """ Test that the database URI is set correctly """
        database_setup = DatabaseSetup(model_metadata, database_uri)
        assert database_setup.database_uri == database_uri

    @staticmethod
    def test_model_metadata(database_uri='sqlite://'):
        """ Test that the model metadata is set correctly """
        database_setup = DatabaseSetup(model_metadata, database_uri)
        assert database_setup.model_metadata == model_metadata

    @staticmethod
    def test_create_database_and_tables(database_uri='sqlite:///test.db'):
        """ Test that the tables are created correctly """
        database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        session = get_database_session(database_uri)
        # noinspection SqlInjection,SqlDialectInspection
        test_table_query = session.execute('SELECT * FROM test_table')
        assert test_table_query.cursor.description[0][0] == 'id'
        assert test_table_query.cursor.description[1][0] == 'super_sophisticated_field'
        database_setup.drop_database()

    @staticmethod
    def test_drop_database(database_uri='sqlite:///test.db'):
        """ Test that the database is dropped correctly """
        database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        assert database_setup.drop_database()
        session = get_database_session(database_uri)
        with pytest.raises(OperationalError):
            # noinspection SqlDialectInspection
            session.execute('SELECT * FROM test_table')
        # Dropping again fails
        assert database_setup.drop_database() is False
