from sqlmodel import Field, SQLModel

class Config(SQLModel, table=True):
    key: str = Field(default=None, primary_key=True)
    value: str = Field(nullable=True)

class Channel(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    uri: str = Field(nullable=False)

class User(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False)

class Asset(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False)
    title: str = Field(nullable=False)
    creator: str = Field(nullable=True)
    subject: str = Field(nullable=True)
    description: str = Field(nullable=True)
