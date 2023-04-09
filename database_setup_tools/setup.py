import threading
from typing import Any, List, Optional, Union

import sqlalchemy_utils
from sqlalchemy import MetaData, Table
from sqlmodel.main import SQLModel, SQLModelMetaclass

from database_setup_tools.session_manager import SessionManager


class DatabaseSetup:
    """Create the database and the tables if not done yet"""

    _instances = []
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._get_cached_instance(args, kwargs):
            with cls._lock:
                if not cls._get_cached_instance(args, kwargs):
                    cls._instances.append((super(cls, cls).__new__(cls), (args, kwargs)))
        return cls._get_cached_instance(args, kwargs)

    def __init__(self, model_metadata: MetaData, database_uri: str, **engine_options: dict[str, Any]):
        """Set up a database based on its URI and metadata. Will not overwrite existing data.

        Args:
            model_metadata (Metadata): The metadata of the models to create the tables for
            database_uri (str): The URI of the database to create the tables for

        Keyword Args:
            **engine_options: Keyword arguments to pass to the engine
        """
        if not isinstance(model_metadata, MetaData):
            raise TypeError("model_metadata must be a MetaData")

        if not isinstance(database_uri, str):
            raise TypeError("database_uri must be a string")

        self._model_metadata = model_metadata
        self._database_uri = database_uri
        self._engine_options = engine_options
        self.create_database()

    @property
    def model_metadata(self) -> MetaData:
        """Getter for the model metadata

        Returns:
            MetaData: The model metadata
        """
        return self._model_metadata

    @property
    def session_manager(self) -> SessionManager:
        """Getter for the session manager

        Returns:
            SessionManager: The session manager
        """
        return SessionManager(database_uri=self.database_uri, **self._engine_options)

    @property
    def database_uri(self) -> str:
        """Getter for the database URI

        Returns:
            str: The database URI
        """
        return self._database_uri

    def drop_database(self) -> bool:
        """Drop the database and the tables if possible

        Returns:
            bool: True if the database was dropped, False otherwise
        """
        if sqlalchemy_utils.database_exists(self.database_uri):
            sqlalchemy_utils.drop_database(self.database_uri)
            return True
        return False

    def create_database(self) -> bool:
        """Create the database and the tables if not done yet"""
        if not sqlalchemy_utils.database_exists(self.database_uri):
            sqlalchemy_utils.create_database(self.database_uri)
            self.model_metadata.create_all(self.session_manager.engine)
            return True
        return False

    def truncate(self, tables: Optional[List[Union[SQLModel, SQLModelMetaclass]]] = None):
        """Truncate all tables in the database"""
        tables_to_truncate: List[Table] = self.model_metadata.sorted_tables
        if tables is not None:
            table_names = [table.__tablename__ for table in tables]
            tables_to_truncate = filter(lambda table: table.name in table_names, tables_to_truncate)

        session = next(self.session_manager.get_session())

        try:
            tables_with_schema = [f"{table.schema or 'public'}.\"{table.name}\"" for table in tables_to_truncate]
            session.execute(f"TRUNCATE TABLE {', '.join(tables_with_schema)} CASCADE;")
            session.commit()
        finally:
            session.close()

    @classmethod
    def _get_cached_instance(cls, args: tuple, kwargs: dict) -> Optional[object]:
        """Provides a cached instance of the SessionManager class if existing"""
        for instance, arguments in cls._instances:
            if arguments == (args, kwargs):
                return instance
        return None
