from pydantic import BaseModel
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
    files: Optional[List[str]] = None
    status : Optional[str] = None
    allow_edit : Optional[str] = None
    kind : str
    icon : Optional[str] = None
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
    messages: Optional[List[MessageBaseSchema]] = None
   
    class Config:
        orm_mode = True
        from_attributes = True
 
class ConversationCreateSchema(ConversationBaseSchema):
    pass
 
class ConversationSchema(ConversationBaseSchema):
    id: str