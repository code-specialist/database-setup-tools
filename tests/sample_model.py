from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    """Customer model"""

    id: int = Field(index=True, primary_key=True)
    name: str


model_metadata = SQLModel.metadata
