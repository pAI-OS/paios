from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Boolean
from backend.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlmodel import Field, Relationship
from backend.db import SQLModelBase

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
    passkey_user_id: str = Field()
    creds: list["PublicKeyCred"] = Relationship(back_populates="owner")
    sessions: list["Session"] = Relationship(back_populates="user")

class PublicKeyCred(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    public_key: str = Field()
    passkey_user_id: str = Field(foreign_key="user.passkey_user_id")
    backed_up: str = Field()
    name: str | None = Field(default=None)
    transports: str | None = Field(default=None)
    owner: User = Relationship(back_populates="creds")

class Session(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    token: str = Field()
    expires_at: datetime = Field()
    user: User = Relationship(back_populates="sessions")

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
