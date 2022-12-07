import random

import uvicorn
from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel, Field

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup

DATABASE_URI = "sqlite:///./test.db"

app = FastAPI()
session_manager = SessionManager(database_uri=DATABASE_URI)


class User(SQLModel, table=True):
    """ Game model """
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
