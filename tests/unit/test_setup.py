from typing import Any, Callable

import pytest
import sqlalchemy_utils
from sqlalchemy.orm.scoping import ScopedSession
from mockito import unstub

import database_setup_tools.session_manager as session_manager_module
from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup
from tests.unit.sample_model import model_metadata


def get_database_session(database_uri: str) -> ScopedSession:
    """ Get a database session """
    session_manager = SessionManager(database_uri)
    return next(session_manager.get_session())


class TestSetup:
    database_uri = 'sqlite://'

    @pytest.fixture
    def database_setup(self, when: Callable) -> DatabaseSetup:
        when(DatabaseSetup) \
            .create_database() \
            .thenReturn(None)

        yield DatabaseSetup(model_metadata=model_metadata, database_uri=self.database_uri)

    def test_database_setup_is_singleton(self, database_setup: DatabaseSetup, when2: Callable):
        assert database_setup is DatabaseSetup(model_metadata=model_metadata, database_uri=self.database_uri)

    def test_create_database_setup_success(self, expect: Callable):
        expect(DatabaseSetup, times=1).create_database()
        DatabaseSetup(model_metadata=model_metadata, database_uri=self.database_uri)

    @pytest.mark.parametrize('invalid_metadata', [None, 'metadata', 42, False])
    def test_create_database_setup_fail_modelmetadata_invalid_type(self, invalid_metadata: Any):
        with pytest.raises(TypeError):
            DatabaseSetup(model_metadata=invalid_metadata, database_uri=self.database_uri)

    @staticmethod
    @pytest.mark.parametrize('invalid_database_uri', [None, model_metadata, 42, False])
    def test_create_database_setup_fail_database_uri_invalid_type(invalid_database_uri: Any):
        with pytest.raises(TypeError):
            DatabaseSetup(model_metadata=model_metadata, database_uri=invalid_database_uri)

    def test_database_uri(self, database_setup: DatabaseSetup):
        assert database_setup.database_uri == self.database_uri

    def test_model_metadata(self, database_setup: DatabaseSetup):
        assert database_setup.model_metadata == model_metadata

    def test_create_database(self, database_setup: DatabaseSetup, when: Callable, expect: Callable):
        unstub()  # remove stub for create_database method

        expect(sqlalchemy_utils, times=1).create_database(self.database_uri)
        expect(database_setup.model_metadata, times=1).create_all(SessionManager(self.database_uri).engine)

        database_setup.create_database()

    def test_drop_database_success(self, database_setup: DatabaseSetup, when: Callable, expect: Callable):
        when(sqlalchemy_utils).database_exists(self.database_uri).thenReturn(True)
        expect(sqlalchemy_utils, times=1).drop_database(self.database_uri)

        assert database_setup.drop_database() is True

    def test_drop_database_fail_not_existing(self, database_setup: DatabaseSetup, when: Callable, expect: Callable):
        when(sqlalchemy_utils).database_exists(self.database_uri).thenReturn(False)
        assert database_setup.drop_database() is False
