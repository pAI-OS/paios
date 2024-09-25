from datetime import datetime
from uuid import uuid4
from sqlmodel import Field, JSON
import sqlalchemy as sa
from backend.db import SQLModelBase
from typing import ClassVar

class Config(SQLModelBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    key: str = Field(index=True)
    value: dict = Field(sa_column=sa.Column(JSON))
    version: int = Field(default=1)
    environment_id: str | None = Field(default=None, foreign_key="environment.id")
    user_id: str | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        sa.UniqueConstraint('key', 'version', 'environment_id', 'user_id', name='uix_key_version_env_user'),
    )

    model_config: ClassVar = {
        "arbitrary_types_allowed": True
    }

class Resource(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    name: str = Field()
    uri: str = Field()

class User(SQLModelBase, table=True):
    id: str = Field(primary_key=True)
    name: str = Field()
    email: str = Field()

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
