from sqlalchemy import Column, String
from backend.db import Base

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)

class Resource(Base):
    __tablename__ = "resource"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    uri = Column(String, nullable=True)
    description = Column(String, nullable=True)
    resource_llm_id = Column(String, nullable=True)
    persona_id = Column(String, nullable=True)
    status = Column(String, nullable=True)
    allow_edit = Column(String, nullable=True)
    kind = Column(String, nullable=False)
    icon= Column(String, nullable=True)
    active= Column(String, nullable=True)

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

class Voice(Base):
    __tablename__ = "voice"
    id = Column(String, primary_key=True)
    xi_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    sample_url = Column(String, nullable=True)

class Face(Base):
    __tablename__ = "face"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class File(Base):
    __tablename__ = "file"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    assistant_id = Column(String, nullable=False)
    num_chunks = Column(String, nullable=False)
    file_id = Column(String, nullable=False)
    indexing_status = Column(String, nullable=False)

class Message(Base):
    __tablename__ = "message"
    id = Column(String, primary_key=True)
    assistant_id = Column(String, nullable=False)
    conversation_id = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    chat_response = Column(String, nullable=False)
    voice_active = Column(String, nullable=False)

class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_timestamp = Column(String, nullable=False)
    last_updated_timestamp = Column(String, nullable=False)
    archive = Column(String, nullable=False)
    assistant_id = Column(String, nullable=False)