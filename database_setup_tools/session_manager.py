import threading
from functools import cached_property
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.scoping import scoped_session


class SessionManager:
    """Manages engines, sessions and connection pools. Thread-safe singleton"""

    _instances = []
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._get_cached_instance(args, kwargs):
            with cls._lock:
                if not cls._get_cached_instance(args, kwargs):
                    cls._instances.append((super(cls, cls).__new__(cls), (args, kwargs)))
        return cls._get_cached_instance(args, kwargs)

    def __init__(self, database_uri: str, **kwargs):
        """Session Manager constructor

        Args:
            database_uri (str): The URI of the database to manage sessions for

        Keyword Args:
            **kwargs: Keyword arguments to pass to the engine

            postgresql:
                pool_size (int): The maximum number of connections to the database
                max_overflow (int): The maximum number of connections to the database
                pre_ping (bool): Whether to ping the database before each connection, may fix connection issues
        """
        if not isinstance(database_uri, str):
            raise TypeError("database_uri must be a string")

        self._database_uri = database_uri
        self._engine = self._get_engine(**kwargs)
        self._session_factory = sessionmaker(self.engine)
        self._Session = scoped_session(self._session_factory)

    @cached_property
    def database_uri(self) -> str:
        """Getter for the database URI"""
        return self._database_uri

    @property
    def engine(self) -> Engine:
        """Getter for the engine"""
        return self._engine

    def get_session(self) -> Generator[Session, None, None]:
        """Provides a (thread safe) scoped session that is wrapped in a context manager"""
        with self._Session() as session:
            yield session

    def _get_engine(self, **kwargs) -> Engine:
        """Provides a database engine"""
        return create_engine(self.database_uri, **kwargs)

    @classmethod
    def _get_cached_instance(cls, args: tuple, kwargs: dict) -> Optional[object]:
        """Provides a cached instance of the SessionManager class if existing"""
        for instance, arguments in cls._instances:
            if arguments == (args, kwargs):
                return instance
        return None
