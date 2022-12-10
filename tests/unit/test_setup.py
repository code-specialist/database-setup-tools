from typing import Any, Callable

import pytest
import sqlalchemy_utils
from mockito import unstub

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup
from tests.unit.sample_model import model_metadata


class TestSetup:

    @pytest.fixture
    def database_uri(self) -> str:
        return 'sqlite://'

    @pytest.fixture
    def database_setup(self, when: Callable, database_uri: str) -> DatabaseSetup:
        when(DatabaseSetup) \
            .create_database() \
            .thenReturn(None)

        yield DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)

    @pytest.mark.parametrize("database_uri", ["sqlite://", "postgresql://"])
    def test_database_setup_is_singleton_with_same_arguments(self, database_setup: DatabaseSetup, database_uri: str):
        assert database_setup is DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)

    def test_database_setup_is_singleton_with_different_arguments(self, database_setup: DatabaseSetup):
        database_uri_1, database_uri_2 = 'sqlite://', 'postgresql://'
        assert DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri_1) is not DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri_2)

    def test_create_database_setup_success(self, expect: Callable, database_uri: str):
        expect(DatabaseSetup, times=1).create_database()
        DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)

    @pytest.mark.parametrize('invalid_metadata', [None, 'metadata', 42, False])
    def test_create_database_setup_fail_modelmetadata_invalid_type(self, invalid_metadata: Any, database_uri: str):
        with pytest.raises(TypeError):
            DatabaseSetup(model_metadata=invalid_metadata, database_uri=database_uri)

    @staticmethod
    @pytest.mark.parametrize('invalid_database_uri', [None, model_metadata, 42, False])
    def test_create_database_setup_fail_database_uri_invalid_type(invalid_database_uri: Any):
        with pytest.raises(TypeError):
            DatabaseSetup(model_metadata=model_metadata, database_uri=invalid_database_uri)

    def test_database_uri(self, database_setup: DatabaseSetup, database_uri: str):
        assert database_setup.database_uri == database_uri

    def test_model_metadata(self, database_setup: DatabaseSetup):
        assert database_setup.model_metadata == model_metadata

    def test_create_database(self, database_setup: DatabaseSetup, database_uri: str, when: Callable, expect: Callable):
        unstub()  # remove stub for create_database method

        expect(sqlalchemy_utils, times=1).create_database(database_uri)
        expect(database_setup.model_metadata, times=1).create_all(SessionManager(database_uri).engine)

        database_setup.create_database()

    def test_drop_database_success(self, database_setup: DatabaseSetup, database_uri: str, when: Callable, expect: Callable):
        when(sqlalchemy_utils).database_exists(database_uri).thenReturn(True)
        expect(sqlalchemy_utils, times=1).drop_database(database_uri)

        assert database_setup.drop_database() is True

    def test_drop_database_fail_not_existing(self, database_setup: DatabaseSetup, database_uri: str, when: Callable, expect: Callable):
        when(sqlalchemy_utils).database_exists(database_uri).thenReturn(False)
        assert database_setup.drop_database() is False
