from uuid import uuid4
from threading import Lock
from sqlalchemy import select, delete
from backend.models import Message, Conversation, Resource
from backend.db import db_session_context
from backend.schemas import MessageSchema, MessageCreateSchema
from typing import Tuple, Optional
from backend.utils import get_current_timestamp
from backend.managers.RagManager import RagManager
from langchain_community.llms import Ollama
import os
from dotenv import load_dotenv, set_key
from common.paths import base_dir

class MessagesManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MessagesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, max_tokens=None, temperature=None, top_k=None, top_p=None):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True
                    load_dotenv(base_dir / '.env')
                    self.max_tokens = max_tokens if max_tokens else self.get_model_params('MAX_TOKENS')
                    self.temperature = temperature if temperature else self.get_model_params('TEMPERATURE')
                    self.top_k = top_k if top_k else self.get_model_params('TOP_K')
                    self.top_p = top_p if top_p else self.get_model_params('TOP_P')
                    
    def get_model_params(self, param_name: str):
        if param_name == 'MAX_TOKENS':
            max_tokens=os.environ.get('MAX_TOKENS')       
            if not max_tokens:                 
                max_tokens = 1000000
            set_key(base_dir / '.env', 'MAX_TOKENS', str(max_tokens))            
            return max_tokens
        
        if param_name == 'TEMPERATURE':            
            temperature=os.environ.get('TEMPERATURE')
            if not temperature:
                temperature = 0.2
            set_key(base_dir / '.env', 'TEMPERATURE', str(temperature))
            return temperature
        
        if param_name == 'TOP_K':
            top_k=os.environ.get('TOP_K')
            if not top_k:                
                top_k = 10              
            set_key(base_dir / '.env', 'TOP_K', str(top_k))        
            return top_k
        
        if param_name == 'TOP_P':
            top_p=os.environ.get('TOP_P')
            if not top_p:                
                top_p = 0.5
                print("top_p", str(top_p))
            set_key(base_dir / '.env', 'TOP_P', str(top_p))        
            return top_p
                        
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
        
    def set_max_tokens(self, max_tokens: int):
        self.max_tokens = max_tokens

    async def create_message(self, message_data: MessageCreateSchema) -> Tuple[Optional[str], Optional[str]]:
        try:
            async with db_session_context() as session:
                timestamp = get_current_timestamp()
                
                conversation_id = message_data.get('conversation_id')
                
                if conversation_id:
                    result = await session.execute(select(Conversation).filter(Conversation.id == conversation_id))
                    conversation = result.scalar_one_or_none()
                    if not conversation:
                        return None, "Conversation not found"
                    
                    conversation.last_updated_timestamp = timestamp
                
                model_name, error_message = await self.__get_llm_name__(message_data['assistant_id'])
                if error_message:
                    return None, error_message
                
                llm = Ollama(model=model_name, 
                             num_predict=int(self.max_tokens), 
                             temperature=float(self.temperature), 
                             top_k=int(self.top_k), 
                             top_p=float(self.top_p))
                
                assistant_id = message_data['assistant_id']
                query = message_data['prompt']
                rm = RagManager()
                response = await rm.retrieve_and_generate(assistant_id, query, llm)
                chat_response = response["answer"]

                if conversation_id:
                    message_data['chat_response'] = chat_response
                    message_data['timestamp'] = timestamp

                    new_message = Message(id=str(uuid4()), **message_data)
                    session.add(new_message)
                    await session.commit()
                    await session.refresh(new_message)
                    return new_message.id, None
                else:
                    return chat_response, None
        
        except Exception as e:
            return None, f"An unexpected error occurred while creating a message: {str(e)}"

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
                    voice_active=message.voice_active             
                )
            return None
    
    def extract_names_from_uri(self, uri):
        # Extract the last part of the URI after the last "/"
        model_name = uri.split('/')[-1] 
        return model_name
        
    async def delete_messages_from_conversation(self, conversation_id):
        async with db_session_context() as session:
            stmt = select(Message).filter(Message.conversation_id == conversation_id) 
            result = await session.execute(stmt)
            msgs = result.scalars().all()
            msgs = [MessageSchema.from_orm(msg) for msg in msgs]
            print("msgs: ", msgs)
            for msg in msgs:
                if not await self._delete_message(msg.id):
                    return False
            return True

    async def _delete_message(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Message).where(Message.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0