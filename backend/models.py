from sqlmodel import Field, SQLModel

class Config(SQLModel, table=True):
    key: str = Field(default=None, primary_key=True)
    value: str

class Channel(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    uri: str
