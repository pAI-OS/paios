from datetime import datetime
from pydantic import BaseModel, field_serializer
from typing import Optional, List


# We have *Create schemas because API clients ideally don't set the id field, it's set by the server
# Alternatively we could have made the id optional but then we would have to check if it's set by the client

# Config schemas
class ConfigBaseSchema(BaseModel):
    value: Optional[str] = None

class ConfigSchema(ConfigBaseSchema):
    key: str

# Resource schemas
class ResourceBaseSchema(BaseModel):
    name: str
    uri: Optional[str] = None
    description: Optional[str] = None
    resource_llm_id : Optional[str] = None
    persona_id : Optional[str] = None    
    status : Optional[str] = None
    allow_edit : Optional[str] = None
    kind : str
    icon : Optional[str] = None
    active : Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True

class ResourceCreateSchema(ResourceBaseSchema):
    pass

class ResourceSchema(ResourceBaseSchema):
    id: str

# Persona schemas
class PersonaBaseSchema(BaseModel):
    name: str
    description: Optional[str] = None
    voice_id: str = None
    face_id: str = None
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

# Share schemas
class ShareBaseSchema(BaseModel):
    resource_id: str
    user_id: Optional[str] = None
    expiration_dt: Optional[datetime] = None
    is_revoked: Optional[bool] = False

    @field_serializer('user_id')
    def serialize_user_id(self, user_id: str, _info):
        if user_id:
            return user_id
        else:
            return ""

    @field_serializer('expiration_dt', when_used='unless-none')
    def serialize_expiration_dt(self, dt: datetime, _info):
        if dt:
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

class ShareCreateSchema(ShareBaseSchema):
    pass

class ShareSchema(ShareBaseSchema):
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
    
# Voice schemas
class VoiceBaseSchema(BaseModel):
    xi_id: str
    name: str
    text_to_speak: Optional[str] = None
    image_url: Optional[str] = None
    sample_url: Optional[str] = None
    msg_id: Optional[str] = None        
    audio_msg_path: Optional[str] = None                 
    class Config:
        orm_mode = True
        from_attributes = True

class VoiceCreateSchema(VoiceBaseSchema):
    pass

class VoiceSchema(VoiceBaseSchema):
    id:str

# Face schemas
class FaceBaseSchema(BaseModel):
    name: str

class FaceCreateSchema(FaceBaseSchema):
    id: str

class FaceSchema(FaceBaseSchema):
    pass

# Document schemas
class DocsPathsBaseSchema(BaseModel):
    docs_paths: Optional[List[str]] = None

class DocsPathsCreateSchema(DocsPathsBaseSchema):
    pass

class DocsPathsSchema(DocsPathsBaseSchema):
    id: str

# Message schemas
class MessageBaseSchema(BaseModel):
    conversation_id: str
    assistant_id: str
    timestamp: str
    prompt: str
    chat_response: str
    voice_active: str    
    class Config:
        orm_mode = True
        from_attributes = True

class MessageCreateSchema(MessageBaseSchema):
    pass

class MessageSchema(MessageBaseSchema):
    id: str

# Conversation schemas
class ConversationBaseSchema(BaseModel):
    name: str
    created_timestamp: str
    last_updated_timestamp: str
    archive: str
    assistant_id: str
    messages: Optional[List[MessageSchema]] = None
   
    class Config:
        orm_mode = True
        from_attributes = True
 
class ConversationCreateSchema(ConversationBaseSchema):
    pass
 
class ConversationSchema(ConversationBaseSchema):
    id: str

# File schemas
class FileBaseSchema(BaseModel):
    name: str
    num_chunks: str
    file_id: str
    indexing_status: str
    class Config:
        orm_mode = True
        from_attributes = True

class FileCreateSchema(FileBaseSchema):
    pass

class FileSchema(FileBaseSchema):
    id: str