from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model"""

    id: int = Field(index=True, primary_key=True)
    name: str


model_metadata = SQLModel.metadata
