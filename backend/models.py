from sqlalchemy import Column, String, ForeignKey
from backend.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

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

class Asset(Base):
    __tablename__ = "asset"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    creator = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    description = Column(String, nullable=True)

class Session(Base):
    __tablename__ = "session"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="sessions")