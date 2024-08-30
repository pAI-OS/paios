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
                    
    async def __get_llm_name__(self, assistant_id) -> Tuple[Optional[str], Optional[str]]:
        async with db_session_context() as session:
            result = await session.execute(select(Resource).filter(Resource.id == assistant_id))
            assistant = result.scalar_one_or_none()
            if not assistant:
                return None, "Assistant not found"
            
            llm_id = assistant.resource_llm_id
            result = await session.execute(select(Resource).filter(Resource.id == llm_id))
            llm = result.scalar_one_or_none()
            if not llm:
                return None, "LLM resource not found"
            
            return self.extract_names_from_uri(llm.uri.split('/')[-1]), None
        

    async def create_message(self, message_data: MessageCreateSchema) -> Tuple[Optional[str], Optional[str]]:
        try:
            async with db_session_context() as session:
                timestamp = get_current_timestamp()
                
                conversation_id = message_data.get('conversation_id')
                
                if conversation_id:  # If conversation_id is provided, proceed as usual
                    result = await session.execute(select(Conversation).filter(Conversation.id == conversation_id))
                    conversation = result.scalar_one_or_none()
                    if not conversation:
                        return None, "Conversation not found"
                    
                    conversation.last_updated_timestamp = timestamp
                
                model_name, error_message = await self.__get_llm_name__(message_data['assistant_id'])
                if error_message:
                    return None, error_message
                
                llm = Ollama(model=model_name)
                
                assistant_id = message_data['assistant_id']
                query = message_data['prompt']
                rm = RagManager()
                response = await rm.retrieve_and_generate(assistant_id, query, llm)
                chat_response = response["answer"]
                
                if conversation_id:  # If conversation_id is provided, create a new message
                    message_data["chat_response"] = chat_response
                    message_data['timestamp'] = timestamp
                    
                    new_message = Message(id=str(uuid4()), **message_data)
                    session.add(new_message)
                    await session.commit()
                    await session.refresh(new_message)
                    return new_message.id, None
                else:  # If conversation_id is not provided, return chat_response only
                    return chat_response, None
        
        except Exception as e:
            # Handle any unexpected errors
            return None, f"An unexpected error occurred: {str(e)}"

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