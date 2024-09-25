from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any

# We have *Create schemas because API clients ideally don't set the id field, it's set by the server
# Alternatively we could have made the id optional but then we would have to check if it's set by the client

# TODO: Consider enforcing fields using patterns

# Config schemas
class ConfigBaseSchema(BaseModel):
    key: str
    value: Any
    version: int = Field(default=1)
    user_id: Optional[str] = None

class ConfigSchema(ConfigBaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime

class ConfigCreateSchema(ConfigBaseSchema):
    pass

# Resource schemas
class ChannelBaseSchema(BaseModel):
    name: str
    uri: str

class ChannelCreateSchema(ChannelBaseSchema):
    pass

class ChannelSchema(ChannelBaseSchema):
    id: str

# Persona schemas
class PersonaBaseSchema(BaseModel):
    name: str
    description: Optional[str] = None
    voice_id: Optional[str] = None
    face_id: Optional[str] = None

class PersonaCreateSchema(PersonaBaseSchema):
    pass

class PersonaSchema(PersonaBaseSchema):
    id: str

# Resource schemas
class ResourceBaseSchema(BaseModel):
    name: str
    uri: str

class ResourceCreateSchema(ResourceBaseSchema):
    pass

class ResourceSchema(ResourceBaseSchema):
    id: str

# User schemas
class UserBaseSchema(BaseModel):
    name: str
    email: str

class UserCreateSchema(UserBaseSchema):
    pass

class UserSchema(UserBaseSchema):
    id: str

# Asset schemas
class AssetBaseSchema(BaseModel):
    title: str
    user_id: Optional[str] = None
    creator: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None

class AssetCreateSchema(AssetBaseSchema):
    pass

class AssetSchema(AssetBaseSchema):
    id: str

# Share schemas

class ShareBaseSchema(BaseModel):
    resource_id: str
    user_id: Optional[str] = None
    expiration_dt: Optional[datetime] = None
    is_revoked: bool = Field(default=False)

class ShareCreateSchema(ShareBaseSchema):
    pass

class ShareSchema(ShareBaseSchema):
    id: str
