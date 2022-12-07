import sqlalchemy as sqla
import threading
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import ScopedSession, scoped_session
from typing import Iterator


class SessionManager:
    """ Manages engines, sessions and connection pools. Thread-safe singleton """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, database_uri: str, **kwargs):
        """ Session Manager constructor

        Args:
            database_uri (str): The URI of the database to manage sessions for

        Keyword Args:
            **kwargs: Keyword arguments to pass to the engine

            postgresql:
                pool_size (int): The maximum number of connections to the database
                max_overflow (int): The maximum number of connections to the database
                pre_ping (bool): Whether to ping the database before each connection, may fix connection issues
        """
        self._database_uri = database_uri
        self._engine = self._get_engine(**kwargs)
        self._session_factory = sessionmaker(self.engine)
        self._Session = scoped_session(self._session_factory)

    @property
    def database_uri(self) -> str:
        """ Getter for the database URI """
        return self._database_uri

    @property
    def engine(self) -> Engine:
        """ Getter for the engine """
        return self._engine

    def get_session(self) -> Iterator[ScopedSession]:
        """ Provides a (thread safe) scoped session that is wrapped in a context manager """
        with self._Session() as session:
            yield session

    def _get_engine(self, **kwargs) -> Engine:
        """ Provides a database engine """
        return sqla.create_engine(self.database_uri, **kwargs)
