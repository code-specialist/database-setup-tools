from contextlib import contextmanager
from typing import Callable, Any

import pytest as pytest
from sqlalchemy.engine import Engine

from database_setup_tools.session_manager import SessionManager


class TestSessionManager:
    @pytest.fixture
    def database_uri(self) -> str:
        return "sqlite://"

    @pytest.fixture
    def session_manager(self, database_uri: str) -> SessionManager:
        yield SessionManager(database_uri=database_uri)

    @pytest.mark.parametrize("invalid_database_uri", [None, (), 42, False])
    def test_create_session_manager_fail_invalid_database_uri_type(self, invalid_database_uri: Any):
        with pytest.raises(TypeError):
            SessionManager(database_uri=invalid_database_uri)

    @pytest.mark.parametrize("database_uri", ["sqlite://", "postgresql://"])
    def test_session_manager_is_singleton_with_same_arguments(self, database_uri: str):
        assert SessionManager(database_uri=database_uri) is SessionManager(database_uri=database_uri)

    def test_session_manager_singletons_with_different_arguments(self):
        database_uri_1, database_uri_2 = "sqlite://", "postgresql://"
        assert SessionManager(database_uri=database_uri_1) is not SessionManager(database_uri=database_uri_2)

    def test_database_uri(self, session_manager: SessionManager, database_uri: str):
        assert session_manager.database_uri == database_uri

    @pytest.mark.parametrize("database_uri, name, driver", [("sqlite://", "sqlite", "pysqlite"), ("postgresql+psycopg2://", "postgresql", "psycopg2")])
    def test_engine(self, database_uri: str, name: str, driver: str):
        session_manager = SessionManager(database_uri)
        assert isinstance(session_manager.engine, Engine)
        assert session_manager.engine.name == name
        assert session_manager.engine.driver == driver

    def test_get_session(self, session_manager: SessionManager, database_uri: str, when: Callable):
        @contextmanager
        def mocked_session():
            try:
                yield "mocked session"
            finally:
                pass

        when(session_manager)._Session().thenReturn(mocked_session())

        assert next(session_manager.get_session()) == "mocked session"
