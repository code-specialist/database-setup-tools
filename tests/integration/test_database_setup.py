import pytest
from starlette.testclient import TestClient

from database_setup_tools import DatabaseSetup
from tests.integration.example.app import app, model_metadata, DATABASE_URI

database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=DATABASE_URI)


class TestIntegrationDatabaseSetup:

    @pytest.fixture
    def test_client(self) -> TestClient:
        return TestClient(app)

    @pytest.fixture(scope="function", autouse=True)
    def setup(self):
        database_setup.drop_database()
        database_setup.create_database()

    def test_get_all_users(self, test_client: TestClient):
        response = test_client.get('/users/')
        assert response.status_code == 200
        assert response.json() == []

    def test_add_random_user(self, test_client: TestClient):
        response = test_client.post('/users/')
        assert response.status_code == 200

        assert test_client.get('/users/').json() == [response.json()]