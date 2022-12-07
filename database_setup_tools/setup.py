import threading

import sqlalchemy_utils
from sqlalchemy import MetaData

from database_setup_tools import SessionManager


class DatabaseSetup:
    """ Create the database and the tables if not done yet """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseSetup, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_metadata: MetaData, database_uri: str):
        """ Set up a database based on its URI and metadata. Will not overwrite existing data.

        Args:
            model_metadata (Metadata): The metadata of the models to create the tables for
            database_uri (str): The URI of the database to create the tables for

        """
        self._model_metadata = model_metadata
        self._database_uri = database_uri
        self.create_database()

    @property
    def model_metadata(self) -> MetaData:
        """ Getter for the model metadata

        Returns:
            MetaData: The model metadata
        """
        return self._model_metadata

    @property
    def database_uri(self) -> str:
        """ Getter for the database URI

        Returns:
            str: The database URI
        """
        return self._database_uri

    def drop_database(self) -> bool:
        """ Drop the database and the tables if possible

        Returns:
            bool: True if the database was dropped, False otherwise
        """
        if sqlalchemy_utils.database_exists(self.database_uri):
            sqlalchemy_utils.drop_database(self.database_uri)
            return True
        return False

    def create_database(self):
        """ Create the database and the tables if not done yet """
        sqlalchemy_utils.create_database(self.database_uri)
        session_manager = SessionManager(self.database_uri)
        self.model_metadata.create_all(session_manager.engine)
