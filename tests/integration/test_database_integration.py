from typing import Iterator

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from database_setup_tools.setup import DatabaseSetup
from tests.integration.database_config import DATABASE_URIS
from tests.sample_model import Customer, model_metadata


@pytest.mark.parametrize("database_uri", DATABASE_URIS)
class TestDatabaseIntegration:
    #
    # Fixtures
    #

    @pytest.fixture
    def database_setup(self, database_uri: str) -> DatabaseSetup:
        setup = DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
        setup.drop_database()
        setup.create_database()
        yield setup
        setup.drop_database()

    @pytest.fixture
    def session(self, database_setup: DatabaseSetup) -> Iterator[Session]:
        """Get a database session"""
        return next(database_setup.session_manager.get_session())

    @pytest.fixture
    def delivery_table(self, session: Session) -> str:
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
            session.execute(statement)

        return "delivery"

    @pytest.fixture
    def standalone_table(self, session: Session) -> str:
        setup_statements = [
            "CREATE TABLE standalone (id INTEGER, PRIMARY KEY(id))",
            'SELECT * FROM "standalone"',
            'INSERT INTO "standalone" VALUES (1)',
        ]

        for statement in setup_statements:
            session.execute(statement)

        return "standalone"

    #
    # Tests
    #

    def test_create_database_and_tables(self, database_setup: DatabaseSetup, session: Session):
        """Test that the tables are created correctly"""
        session.execute(f"SELECT * FROM {Customer.__tablename__}")

    def test_create_database_multiple_times(self, database_setup: DatabaseSetup, session: Session):
        """Test that creating the database multiple times does not cause problems"""
        database_setup.create_database()
        session.execute(f"SELECT * FROM {Customer.__tablename__}")

    def test_drop_database(self, database_setup: DatabaseSetup, session: Session):
        """Test that the database is dropped correctly"""
        assert database_setup.drop_database() is True

        with pytest.raises(OperationalError):
            session.execute(f"SELECT * FROM {Customer.__tablename__}")

        assert database_setup.drop_database() is False

    def test_truncate_all_tables(self, database_setup: DatabaseSetup, session: Session, delivery_table: str):
        """Test that all tables are truncated correctly"""

        assert session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 1
        assert session.execute(f'SELECT * FROM "{delivery_table}"').rowcount == 1
        session.commit()

        database_setup.truncate()

        assert session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 0
        assert session.execute(f'SELECT * FROM "{delivery_table}"').rowcount == 0

    def test_truncate_custom_tables(self, database_setup: DatabaseSetup, session: Session, delivery_table: str, standalone_table: str):
        """Test that only specified tables are truncated correctly"""

        assert session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 1
        assert session.execute(f'SELECT * FROM "{delivery_table}"').rowcount == 1
        session.commit()

        database_setup.truncate(tables=[Customer])

        assert session.execute(f"SELECT * FROM {Customer.__tablename__}").rowcount == 0
        assert session.execute(f'SELECT * FROM "{delivery_table}"').rowcount == 0
        assert session.execute(f'SELECT * FROM "{standalone_table}"').rowcount == 1
