# Database tools

Easy to understand and use tools that help you to create databases and interact with them.

## Installation

```bash
pip install database-setup-tools
```

## Features
- **Database creation on app startup**
- Thread-safe database **session manager**
- Opinionated towards `FastAPI` and `SQLModel` but feasible with any other framework or pure `sqlalchemy`
- Easily use a local database in your tests

## Planned features
- Database migrations with `Alembic`

## Example

```python
import random

import uvicorn
from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel, Field

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup

DATABASE_URI = "sqlite:///test.db"

app = FastAPI()
session_manager = SessionManager(database_uri=DATABASE_URI)


class User(SQLModel, table=True):
    """ User model """
    id: int = Field(index=True, primary_key=True)
    name: str


model_metadata = SQLModel.metadata


@app.post('/users/', response_model=User)
def add_random_user(session: Session = Depends(session_manager.get_session)):
    """ Endpoint to add a user with a random name """
    user = User(name=f'User {random.randint(0, 100)}')
    session.add(user)
    session.commit()
    return user


@app.get('/users/', response_model=list[User])
def get_all_users(session: Session = Depends(session_manager.get_session)):
    """ Endpoint to get all users """
    return session.query(User).all()


if __name__ == '__main__':
    database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=DATABASE_URI)
    uvicorn.run(app, host='0.0.0.0', port=8080)
```

 *See  [tests/integration/example/app.py](tests/integration/example/app.py)

## Example for pytest

**conftest.py**
```python
database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=DATABASE_URI)

def pytest_sessionstart(session):
    database_setup.drop_database()
    database_setup.create_database()
```

**test_users.py**
```python
session_manager = SessionManager(database_uri=DATABASE_URI)

@pytest.fixture
def session():
	with session_manager.get_session() as session:
		yield session

def test_create_user(session: Session):
	user = User(name='Test User')
	session.add(user)
	session.commit()
	assert session.query(User).count() == 1
	assert session.query(User).first().name == 'Test User'
```