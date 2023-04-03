from typing import Iterator

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.scoping import ScopedSession
from sqlmodel import Field, SQLModel

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup
from tests.integration.database_config import DATABASE_URIS
from tests.sample_model import Customer, model_metadata


@pytest.mark.parametrize("database_uri", DATABASE_URIS)
class TestDatabaseIntegration:
    @pytest.fixture
    def database_setup(self, database_uri: str) -> DatabaseSetup:
        setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        setup.drop_database()
        setup.create_database()
        yield setup
        setup.drop_database()

    @pytest.fixture
    def database_session(self, database_setup: DatabaseSetup) -> Iterator[ScopedSession]:
        """Get a database session"""
        return next(database_setup.session_manager.get_session())

    def test_create_database_and_tables(self, database_setup: DatabaseSetup, database_session: ScopedSession):
        """Test that the tables are created correctly"""
        database_session.execute(f"SELECT * FROM {Customer.__tablename__}")

    def test_create_database_multiple_times(self, database_setup: DatabaseSetup, database_session: ScopedSession):
        """Test that creating the database multiple times does not cause problems"""
        database_setup.create_database()
        database_session.execute(f"SELECT * FROM {Customer.__tablename__}")

    def test_drop_database(self, database_setup: DatabaseSetup, database_session: ScopedSession):
        """Test that the database is dropped correctly"""
        assert database_setup.drop_database() is True

        with pytest.raises(OperationalError):
            database_session.execute(f"SELECT * FROM {Customer.__tablename__}")

        assert database_setup.drop_database() is False

    def test_truncate_all_tables(self, database_setup: DatabaseSetup, database_session: ScopedSession):
        """Test that all tables are truncated correctly"""

        setup_statements = [
            f"""CREATE TABLE delivery (
                    id INTEGER,
                    name TEXT NOT NULL,
                    customer_id INTEGER,
                    PRIMARY KEY(id),
                    CONSTRAINT fk_user
                        FOREIGN KEY(customer_id)
                            REFERENCES "{Customer.__tablename__}"(id)
                )
            """,
            f'SELECT * FROM "{Customer.__tablename__}"',
            'SELECT * FROM "delivery"',
            f"INSERT INTO \"{Customer.__tablename__}\" VALUES (1, 'John Doe')",
            "INSERT INTO \"delivery\" VALUES (1, 'Delivery 1', 1)",
        ]
        for statement in setup_statements:
            database_session.execute(statement)

        assert database_session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 1
        assert database_session.execute(f'SELECT * FROM "delivery"').rowcount == 1
        database_session.commit()

        database_setup.truncate()

        assert database_session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 0
        assert database_session.execute(f'SELECT * FROM "delivery"').rowcount == 0

    def test_truncate_custom_tables(self, database_uri: str):
        """Test that only specified tables are truncated correctly"""

        class TableToTruncate(SQLModel, table=True):
            id: int = Field(index=True, primary_key=True)
            name: str

        setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        setup.drop_database()
        setup.create_database()
        database_session = next(setup.session_manager.get_session())

        setup_statements = [
            f'SELECT * FROM "{Customer.__tablename__}"',
            f'SELECT * FROM "{TableToTruncate.__tablename__}"',
            f"INSERT INTO \"{Customer.__tablename__}\" VALUES (1, 'John Doe')",
            f"INSERT INTO \"{TableToTruncate.__tablename__}\" VALUES (1, 'Test')",
        ]
        for statement in setup_statements:
            database_session.execute(statement)

        assert database_session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 1
        assert database_session.execute(f'SELECT * FROM "{TableToTruncate.__tablename__}"').rowcount == 1
        database_session.commit()

        setup.truncate(tables=[TableToTruncate])

        assert database_session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 1
        assert database_session.execute(f'SELECT * FROM "{TableToTruncate.__tablename__}"').rowcount == 0
