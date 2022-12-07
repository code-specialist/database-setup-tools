from sqlmodel import SQLModel, Field


class TestTable(SQLModel, table=True):
    """ Test table """
    __tablename__ = 'test_table'
    id: int = Field(primary_key=True)
    super_sophisticated_field: str


model_metadata = SQLModel.metadata
