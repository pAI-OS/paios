from datetime import datetime
from sqlmodel import Field, ForeignKey
from backend.db import SQLModelBase
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

class Config(SQLModelBase, table=True):
    key: str = Field(primary_key=True)
    value: str | None = Field(default=None)

class Resource(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    name: str = Field()
    uri: str = Field()

class User(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    name: str = Field()
    email: str = Field()
    passkey_user_id = Field()
    creds = relationship('Cred', backref='owner')
    sessions = relationship('Session', back_populates='user')

class Cred(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    public_key: str = Field()
    passkey_user_id: str = Field(foreign_key="user.passkey_user_id")
    backed_up: str = Field()
    name: str | None = Field(default=None)
    transports: str = Field()

class Session(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    token: str = Field()
    expires_at: datetime = Field()
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

class Share(SQLModelBase, table=True):
    id: str = Field(primary_key=True)  # the short URL tag, eg abc-def-ghi
    resource_id: str = Field(foreign_key="resource.id")  # the bot ID
    user_id: str | None = Field(default=None)  # the user granted access (optional)
    expiration_dt: datetime | None = Field(default=None)  # the link expiration date/time (optional)
    is_revoked: bool = Field()
