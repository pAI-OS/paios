from uuid import uuid4
from datetime import datetime
from sqlmodel import Field, Relationship, Column, JSON
from backend.db import SQLModelBase
from typing import List, Optional, ForwardRef, Dict, Any

# Forward references
UserRef = ForwardRef("User")
CredRef = ForwardRef("Cred")
SessionRef = ForwardRef("Session")

class Config(SQLModelBase, table=True):
    key: str = Field(primary_key=True)
    value: str | None = Field(default=None)

class Resource(SQLModelBase, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str = Field()
    uri: str = Field()

class User(SQLModelBase, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    webauthn_user_id: str = Field(unique=True, default_factory=lambda: str(uuid4()))
    name: Optional[str] = Field(default=None)
    email: str = Field()
    webauthn_user_id: str = Field()
    creds: List["Cred"] = Relationship(back_populates="user")
    sessions: List["Session"] = Relationship(back_populates="user")

class Cred(SQLModelBase, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    public_key: str = Field()
    webauthn_user_id: str = Field(foreign_key="user.webauthn_user_id")
    backed_up: str = Field()
    name: str | None = Field(default=None)
    transports: str = Field()
    user: "User" = Relationship(back_populates="creds")

class Session(SQLModelBase, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    user_id: str = Field(foreign_key="user.id")
    token: str = Field()
    expires_at: datetime = Field()
    user: User = Relationship(back_populates="sessions")

class Persona(SQLModelBase, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str = Field()
    description: str | None = Field(default=None)
    voice_id: str | None = Field(default=None)
    face_id: str | None = Field(default=None)

class Share(SQLModelBase, table=True):
    id: str = Field(primary_key=True)  # the short URL tag, eg abcd-efgh-ijkl
    resource_id: str = Field(foreign_key="resource.id")  # the bot ID
    user_id: str | None = Field(default=None)  # the user granted access (optional)
    expiration_dt: datetime | None = Field(default=None)  # the link expiration date/time (optional)
    is_revoked: bool = Field()

class Collection(SQLModelBase, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str = Field()
    description: Optional[str] = Field(default=None)
    processor_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

# Resolve forward references
User.model_rebuild()
Cred.model_rebuild()
Session.model_rebuild()
