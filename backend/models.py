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

class Persona(Base):
    __tablename__ = "persona"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    voiceId = Column(String, nullable=True)
    faceId = Column(String, nullable=True)

class Voice(Base):
    __tablename__ = "voice"
    id = Column(String, primary_key=True)
    voice_id = Column(String, nullable=False)
    name = Column(String, nullable=False)

class Face(Base):
    __tablename__ = "face"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
