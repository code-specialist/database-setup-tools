# Database Setup Tools for SQLModel / SQLAlchemy

[![CodeQL](https://github.com/code-specialist/database-setup-tools/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/code-specialist/database-setup-tools/actions/workflows/github-code-scanning/codeql)
[![Test](https://github.com/code-specialist/database-setup-tools/actions/workflows/test.yaml/badge.svg)](https://github.com/code-specialist/database-setup-tools/actions/workflows/test.yaml)

Simplified database lifecycle and session management based on [SQLModel](https://sqlmodel.tiangolo.com/) / [SQLAlchemy](https://www.sqlalchemy.org/).

Any contributions are welcome! But we only accept pull requests that come with tests.

## Installation

```bash
pip install database-setup-tools
```

## Features

- **Database creation on app startup**
- Thread-safe database **session manager**
- Opinionated towards `SQLModel` but feasible with any other framework or pure `sqlalchemy`
- Easily use a local database in your tests

## Usage

In order to use this library, you need some SQLModel or SQLAlchemy tables and a URI to connect to your database.
With this in place, the `DatabaseSetup` instance can be created - which contains all provided tools and also automatically
creates the database including all tables.

```python
from sqlmodel import Field, SQLModel
from database_setup_tools import DatabaseSetup


class User(SQLModel, table=True):
    """ User database entity / table """
    id: int = Field(index=True, primary_key=True)
    name: str


# create database & tables, establish connection with session pool
database_setup = DatabaseSetup(
    model_metadata = SQLModel.metadata,
    database_uri="postgresql+psycopg2://postgres:postgres@localhost:5432/database",
)
```

> Note: The `DatabaseSetup` class acts as singleton, so if you create multiple instances with the same
> set of parameters, you will always get the same instance back instead of creating a new one.

After the setup is created, you can get a scoped session via the provided session manager and use it
for database transactions.

```python
# get scoped session
session = next(database_setup.session_manager.get_session())

# do stuff in session
user = User(name="Alice")
session.add(user)
session.commit()
```

The `DatabaseSetup` instance also provides lifecycle methods allowing to manually control the database:

```python
database_setup.create_database()
database_setup.drop_database()
```

## Development

### Testing

1. Spin up databases for local integration tests: `docker-compose -f tests/docker-compose.yaml up -d`
1. Create virtual environment & install dependencies: `poetry install`
1. Run tests: `poetry run pytest`
