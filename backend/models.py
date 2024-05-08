from sqlmodel import Field, SQLModel

class Config(SQLModel, table=True):
    key: str = Field(default=None, primary_key=True)
    value: str

class Channel(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    uri: str = Field(nullable=False)

class User(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False)
