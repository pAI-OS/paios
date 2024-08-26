from sqlalchemy import Column, String, ForeignKey
from backend.db import Base
from sqlalchemy.types import DateTime, Boolean

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)

class Resource(Base):
    __tablename__ = "resource"
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

class Persona(Base):
    __tablename__ = "persona"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    voice_id = Column(String, nullable=True)
    face_id = Column(String, nullable=True)

class Share(Base):
    __tablename__ = "share"
    key = Column(String, primary_key=True)  # the short URL tag
    resource_id = Column(String, ForeignKey("resource.id"), nullable=False)  # the bot ID
    user_id = Column(String, nullable=True)  # the user granted access (optional)
    expiration_dt = Column(DateTime, nullable=True)  # the link expiration date/time (optional)
    is_revoked = Column(Boolean, nullable=False)