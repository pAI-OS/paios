from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Message, Conversation, Resource
from backend.db import db_session_context
from backend.schemas import MessageSchema, MessageCreateSchema
from typing import List, Tuple, Optional, Dict, Any
from backend.utils import get_current_timestamp
from backend.managers.RagManager import RagManager

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

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
                    
    async def __get_llm_name__(self, assistant_id):
        # Get the llm_id from the assistant_id
        async with db_session_context() as session:
            result = await session.execute(select(Resource).filter(Resource.id == assistant_id))
            assistant = result.scalar_one_or_none()
            llm_id = assistant.resource_llm_id
            result = await session.execute(select(Resource).filter(Resource.id == llm_id))
            llm = result.scalar_one_or_none()                    
            return self.extract_names_from_uri(llm.uri.split('/')[-1])
        

    async def create_message(self, message_data: MessageCreateSchema) -> str:
        async with db_session_context() as session:
            timestamp = get_current_timestamp()
            
            # update conversation last_updated_timestamp
            conversation_id = message_data['conversation_id']
            result = await session.execute(select(Conversation).filter(Conversation.id == conversation_id))
            conversation = result.scalar_one_or_none()
            conversation.last_updated_timestamp = timestamp
            
            model_name = await self.__get_llm_name__(message_data['assistant_id'])
            if model_name is None:
                return None
            llm = Ollama(model=model_name)
            
            assistant_id = message_data['assistant_id']
            query = message_data['prompt']
            rm = RagManager()
            response = await rm.retrive_and_generate(assistant_id, query, llm)
            message_data["chat_response"] = response["answer"]
            message_data['timestamp'] = timestamp
            
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
    
    def extract_names_from_uri(self, uri):
        # Extract the last part of the URI after the last "/"
        model_name = uri.split('/')[-1] 
        return model_name