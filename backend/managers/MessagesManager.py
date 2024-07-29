from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Message
from backend.db import db_session_context
from backend.schemas import MessageSchema, MessageCreateSchema
from typing import List, Tuple, Optional, Dict, Any

class MessagesManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MessagesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True

    async def create_message(self, message_data: MessageCreateSchema) -> str:
        async with db_session_context() as session:
            
            #ToDo: Get chat_response from the assistant
            message_data["chat_response"] = "Assistant response..."
            
            new_message = Message(id=str(uuid4()), **message_data)
            session.add(new_message)
            await session.commit() 
            await session.refresh(new_message)
            return new_message.id    

    async def retrieve_message(self, id:str) -> Optional[MessageSchema]:
        async with db_session_context() as session:            
            result = await session.execute(select(Message).filter(Message.id == id))
            message = result.scalar_one_or_none()
            if message:
                return MessageSchema(
                    id=message.id,
                    assistant_id=message.assistant_id,
                    conversation_id=message.conversation_id,
                    timestamp=message.timestamp,
                    prompt=message.prompt,
                    chat_response=message.chat_response,             
                )
            return None