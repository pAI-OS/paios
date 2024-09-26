from datetime import datetime, timezone
from uuid import uuid4
from sqlmodel import Field
from sqlalchemy import Column, LargeBinary
from backend.db import SQLModelBase
from typing import Any, ClassVar
from . import schemas

# Models inherit from SQLModelBase in db.py and the schemas in schemas.py
# The fields in the schemas are used to generate the columns in the database
# Any database specific configuration should be done here as an overlay of sorts

class Config(SQLModelBase, schemas.ConfigSchema, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    key: str = Field(index=True)
    value: bytes = Field(sa_column=Column(LargeBinary))
    version: int = Field(default=1)
    user_id: str | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    model_config: ClassVar = {
        "arbitrary_types_allowed": True
    }

class Resource(SQLModelBase, schemas.ResourceSchema, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

class User(SQLModelBase, schemas.UserSchema, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

class Asset(SQLModelBase, schemas.AssetSchema, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str | None = Field(default=None, foreign_key="user.id")

class Persona(SQLModelBase, schemas.PersonaSchema, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

class Share(SQLModelBase, schemas.ShareSchema, table=True):
    id: str = Field(primary_key=True)
    resource_id: str = Field(foreign_key="resource.id")
    user_id: str | None = Field(default=None, foreign_key="user.id")
    expiration_dt: datetime | None = Field(default=None)
    is_revoked: bool = Field(default=False)
