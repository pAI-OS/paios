from sqlalchemy import Column, String, ForeignKey
from backend.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlmodel import Field
from backend.db import SQLModelBase

class Config(SQLModelBase, table=True):
    key: str = Field(primary_key=True)
    value: str | None = Field(default=None)

class Resource(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    name: str = Field()
    uri: str = Field()

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    passkey_user_id = Column(String, nullable=False)
    creds = relationship('PublicKeyCred', backref='owner')
    sessions = relationship("Session", back_populates="user")

class PublicKeyCred(Base):
    __tablename__ = "public_key_cred"
    id = Column(String, primary_key=True)
    public_key = Column(String, nullable=False)
    passkey_user_id = Column(String, ForeignKey("user.passkey_user_id"), nullable=False)
    backed_up = Column(String, nullable=False)
    name = Column(String, nullable=True)
    transports = Column(String)

class Session(Base):
    __tablename__ = "session"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="sessions")

class Asset(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    user_id: str | None = Field(default=None, foreign_key="user.id")
    title: str = Field()
    creator: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    description: str | None = Field(default=None)

class Persona(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    name: str = Field()
    description: str | None = Field(default=None)
    voice_id: str | None = Field(default=None)
    face_id: str | None = Field(default=None)
