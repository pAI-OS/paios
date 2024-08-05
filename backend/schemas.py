from pydantic import BaseModel
from typing import Optional

# We have *Create schemas because API clients ideally don't set the id field, it's set by the server
# Alternatively we could have made the id optional but then we would have to check if it's set by the client

# Config schemas
class ConfigBaseSchema(BaseModel):
    value: Optional[str] = None

class ConfigSchema(ConfigBaseSchema):
    key: str

# Channel schemas
class ChannelBaseSchema(BaseModel):
    name: str
    uri: str

class ChannelCreateSchema(ChannelBaseSchema):
    pass

class ChannelSchema(ChannelBaseSchema):
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

class RegistrationOptions(BaseModel):
    email: str

class VerifyRegistration(BaseModel):
    email: str
    att_resp: dict
    challenge: str
    user_id: str

class AuthenticationOptions(BaseModel):
    email: str

class VerifyAuthentication(BaseModel):
    email: str
    auth_resp: dict
    challenge: str
