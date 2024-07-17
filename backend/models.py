from sqlalchemy import Column, String
from backend.db import Base

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)

class Channel(Base):
    __tablename__ = "channel"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    uri = Column(String, nullable=False)

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

class Asset(Base):
    __tablename__ = "asset"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    creator = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    description = Column(String, nullable=True)    

class Persona(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=True)
    voiceId: str = Field(nullable=True)
    faceId: str = Field(nullable=True)
