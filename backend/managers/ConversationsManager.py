from uuid import uuid4
from threading import Lock
from sqlalchemy import select, update, delete, func
from backend.models import Conversation, Resource, Message
from backend.db import db_session_context
from backend.schemas import ConversationSchema, ConversationCreateSchema, MessageSchema
from typing import List, Tuple, Optional, Dict, Any
from backend.utils import get_current_timestamp
 
class ConversationsManager:
    _instance = None
    _lock = Lock()
 
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConversationsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
 
    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True
    
    async def create_conversation(self, resource_id: str, conversation_data: ConversationCreateSchema) -> str:
        async with db_session_context() as session:
            
            if not await self.validate_assistant_id(resource_id):
                return None
            
            timestamp = get_current_timestamp()            
            conversation_data['created_timestamp'] = timestamp
            conversation_data['last_updated_timestamp'] = timestamp            
            conversation_data['archive'] = "False"
            conversation_data['assistant_id'] = resource_id                      
 
            new_conversation = Conversation(id=str(uuid4()), **conversation_data)
            session.add(new_conversation)
            await session.commit()
            await session.refresh(new_conversation)
            return new_conversation.id    
 
    async def update_conversation(self, id: str, conversation_data: ConversationCreateSchema, new_conversation_data) -> Optional[ConversationSchema]:
        async with db_session_context() as session:     
            timestamp = get_current_timestamp()
            conversation_data_dict = conversation_data.dict()
            conversation_data_dict['last_updated_timestamp'] = timestamp
            conversation_data_dict['archive'] = new_conversation_data['archive']
            conversation_data_dict['name'] = new_conversation_data['name']
           
            stmt = update(Conversation).where(Conversation.id == id).values(**conversation_data_dict)
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_conversation = await session.get(Conversation, id)
                return ConversationSchema(
                    id=updated_conversation.id,
                    name=updated_conversation.name,
                    created_timestamp=updated_conversation.created_timestamp,
                    last_updated_timestamp=updated_conversation.last_updated_timestamp,
                    archive=updated_conversation.archive,
                    assistant_id=updated_conversation.assistant_id
                )
            return None
 
    async def delete_conversation(self, id) -> bool:
        async with db_session_context() as session:
            stmt = delete(Conversation).where(Conversation.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
 
    async def retrieve_conversation(self, id: str) -> Optional[ConversationSchema]:
        async with db_session_context() as session:
            # Retrieve the conversation and associated messages in a single query using a join
            result = await session.execute(
                select(Conversation, Message)
                .outerjoin(Message, Message.conversation_id == Conversation.id)
                .filter(Conversation.id == id)
            )

            conversation = None
            messages_list = []

            for conversation_row, message in result.all():
                if not conversation:
                    conversation = conversation_row
                if message:
                    messages_list.append(MessageSchema.from_orm(message))

            if conversation:
                return ConversationSchema(
                    id=conversation.id,
                    name=conversation.name,
                    created_timestamp=conversation.created_timestamp,
                    last_updated_timestamp=conversation.last_updated_timestamp,
                    archive=conversation.archive,
                    assistant_id=conversation.assistant_id,
                    messages=messages_list
                )
            return None

 
    async def retrieve_conversations(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                                sort_order:str = 'asc',  filters: Optional[Dict[str, Any]] = None) -> Tuple[List[ConversationSchema], int]:
        async with db_session_context() as session:
            query = select(Conversation)
 
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        query = query.filter(Conversation.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        query = query.filter(getattr(Conversation, key).in_(value))
                    else:
                        query = query.filter(getattr(Conversation, key) == value)
 
            if sort_by and sort_by in ['id', 'name', 'archive', 'assistant_id']:
                order_column = getattr(Conversation, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)
 
            query = query.offset(offset).limit(limit)
 
            result = await session.execute(query)
            conversations = result.scalars().all()
 
            conversations = [ConversationSchema.from_orm(conversation) for conversation in conversations]
 
            # Get total count
            count_query = select(func.count()).select_from(Conversation)
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        count_query = count_query.filter(Conversation.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        count_query = count_query.filter(getattr(Conversation, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Conversation, key) == value)
 
            total_count = await session.execute(count_query)
            total_count = total_count.scalar()
 
            return conversations, total_count
        
    async def validate_assistant_id(self, assistant_id: str) -> bool:
        async with db_session_context() as session:
            result = await session.execute(select(Resource).filter(Resource.id == assistant_id))
            return result.scalar_one_or_none() is not None