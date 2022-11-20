import threading
from typing import Iterator

import sqlalchemy as sqla
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import ScopedSession, scoped_session


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
                pre_ping (bool): Whether to ping the database before each connection
        """
        self.database_uri = database_uri
        self.engine = self.get_engine(**kwargs)
        self.session_factory = sessionmaker(self.engine)
        self.Session = scoped_session(self.session_factory)

    def get_session(self) -> Iterator[ScopedSession]:
        """ Provides a (thread safe) scoped session that is wrapped in a context manager """
        with self.Session() as session:
            yield session

    def get_engine(self, **kwargs) -> Engine:
        """ Provides a database engine with a maximum of 20 connections and no overflows. This allows up to 20 concurrent  """
        return sqla.create_engine(self.database_uri, **kwargs)
