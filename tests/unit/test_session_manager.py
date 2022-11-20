import pytest as pytest

from database_setup_tools import SessionManager


class TestSessionManager:
    @staticmethod
    @pytest.mark.parametrize('database_uri', ['sqlite://', 'postgresql+psycopg2://'])
    def test_session_manager_is_singleton(database_uri):
        """ Test that the SessionManager is a singleton """
        session_manager_1 = SessionManager(database_uri)
        session_manager_2 = SessionManager(database_uri)
        session_manager_3 = SessionManager(database_uri)
        assert session_manager_1 is session_manager_2 is session_manager_3

    @staticmethod
    @pytest.mark.parametrize('database_uri', ['sqlite://', 'postgresql+psycopg2://'])
    def test_database_uri(database_uri):
        """ Test that the database URI is set correctly """
        session_manager = SessionManager(database_uri)
        assert session_manager.database_uri == database_uri

    @staticmethod
    @pytest.mark.parametrize('database_uri, name, driver', [
        ('sqlite://', 'sqlite', 'pysqlite'),
        ('postgresql+psycopg2://', 'postgresql', 'psycopg2')
    ])
    def test_engine(database_uri, name, driver):
        """ Test that the engine is set correctly """
        session_manager = SessionManager(database_uri)
        assert session_manager.engine == session_manager._engine
        assert session_manager.engine.name == name
        assert session_manager.engine.driver == driver

    @staticmethod
    def test_get_session_sqlite(database_uri: str = 'sqlite://'):
        """ Test that the session is set correctly and usable """
        session_manager = SessionManager(database_uri)
        session = next(session_manager.get_session())
        assert session.execute('SELECT 1').scalar() == 1

        # Get a new session and try again
        session = next(session_manager.get_session())
        assert session.execute('SELECT 1').scalar() == 1
