from pydantic import BaseModel
from typing import Optional, List


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
    description: Optional[str] = None
    channel_llm_id : Optional[str] = None
    persona_id : Optional[str] = None
    files: Optional[List[str]] = None
    status : Optional[str] = None
    allow_edit : Optional[str] = None
    channel_type : Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True

class ChannelCreateSchema(ChannelBaseSchema):
    pass

class ChannelSchema(ChannelBaseSchema):
    id: str

# Persona schemas
class PersonaBaseSchema(BaseModel):
    name: str
    description: Optional[str] = None
    voiceId: str = None
    faceId: str = None
    class Config:
        orm_mode = True
        from_attributes = True

class PersonaCreateSchema(PersonaBaseSchema):
    pass

class PersonaSchema(PersonaBaseSchema):
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

# Voice schemas
class VoiceBaseSchema(BaseModel):
    voice_id: str
    name: str

class VoiceCreateSchema(VoiceBaseSchema):
    id: str

class VoiceSchema(VoiceBaseSchema):
    pass

# Face schemas
class FaceBaseSchema(BaseModel):
    name: str

class FaceCreateSchema(FaceBaseSchema):
    id: str

class FaceSchema(FaceBaseSchema):
    pass
