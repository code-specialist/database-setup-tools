from random import randint

import pytest
from fastapi import FastAPI, Depends
from sqlmodel import Session
from starlette.testclient import TestClient

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup
from tests.sample_model import model_metadata, User


@pytest.mark.parametrize('database_uri', ["sqlite:///test.db"])
class TestIntegrationDatabaseSetup:

    @pytest.fixture
    def database_setup(self, database_uri: str) -> DatabaseSetup:
        setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        yield setup
        setup.drop_database()

    @pytest.fixture
    def session_manager(self, database_uri: str) -> SessionManager:
        return SessionManager(database_uri=database_uri)

    @pytest.fixture
    def fastapi_app(self, session_manager: SessionManager) -> FastAPI:
        app = FastAPI()

        @app.post('/users/', response_model=User)
        def add_random_user(session: Session = Depends(session_manager.get_session)):
            """ Endpoint to add a user with a random name """
            user = User(name=f'User {randint(0, 100)}')
            session.add(user)
            session.commit()
            return user

        @app.get('/users/', response_model=list[User])
        def get_all_users(session: Session = Depends(session_manager.get_session)):
            """ Endpoint to get all users """
            return session.query(User).all()

        return app

    @pytest.fixture
    def test_client(self, fastapi_app: FastAPI) -> TestClient:
        return TestClient(fastapi_app)

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, database_setup: DatabaseSetup, ):
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
