from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Channel, File
from backend.db import db_session_context
from backend.schemas import ChannelCreateSchema, ChannelSchema
from typing import List, Tuple, Optional, Dict, Any

class ChannelsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ChannelsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    # db.init_db()
                    self._initialized = True

    async def create_channel(self, channel_data: ChannelCreateSchema) -> str:
        channel_data_table={  
                        "name": channel_data["name"], 
                        "uri": channel_data["uri"], 
                        "description": channel_data["description"],
                        "channel_llm_id": channel_data["channel_llm_id"],
                        "persona_id": channel_data["persona_id"],
                        "status": channel_data["status"],
                        "allow_edit": channel_data["allow_edit"],
                        "channel_type": channel_data["channel_type"],
                        "icon": channel_data["icon"]
                    }
        async with db_session_context() as session:
            new_channel = Channel(id=str(uuid4()), **channel_data_table)
            session.add(new_channel)
            await session.commit()
            await session.refresh(new_channel)
            return new_channel.id

    async def update_channel(self, id: str, channel_data: ChannelCreateSchema) -> Optional[ChannelSchema]:
        async with db_session_context() as session:
            channel_data_table={  
                        "name": channel_data["name"], 
                        "uri": channel_data["uri"], 
                        "description": channel_data["description"],
                        "channel_llm_id": channel_data["channel_llm_id"],
                        "persona_id": channel_data["persona_id"],
                        "status": channel_data["status"],
                        "allow_edit": channel_data["allow_edit"],
                        "channel_type": channel_data["channel_type"],
                        "icon": channel_data["icon"]
                    }
            files = channel_data["files"]
            
            for file in files:
                self.update_file(id, file)
            stmt = update(Channel).where(Channel.id == id).values(**channel_data_table)

            result = await session.execute(stmt)

            if result.rowcount > 0:                
                await session.commit()
                updated_channel = await session.get(Channel, id)
                return ChannelSchema(id=updated_channel.id, **channel_data)
            return None

    async def delete_channel(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Channel).where(Channel.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_channel(self, id: str) -> Optional[ChannelSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Channel).filter(Channel.id == id))
            files_result = await session.execute(select(File).filter(File.assistant_id == id))
            files = [file.name for file in files_result.scalars()]
            channel = result.scalar_one_or_none()
            if channel:                
                return ChannelSchema(
                    id=channel.id, 
                    name=channel.name, 
                    uri=channel.uri, 
                    description=channel.description, 
                    channel_llm_id=channel.channel_llm_id,
                    persona_id=channel.persona_id,
                    files=files,
                    status=channel.status,
                    allow_edit=channel.allow_edit,
                    channel_type=channel.channel_type,
                    icon=channel.icon)
            return None

    async def retrieve_channels(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                                sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[ChannelSchema], int]:
        async with db_session_context() as session:            
            query = select(Channel)

            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        query = query.filter(Channel.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        query = query.filter(getattr(Channel, key).in_(value))
                    else:
                        query = query.filter(getattr(Channel, key) == value)
            
            if sort_by and sort_by in ['id', 'name', 'uri','status','allow_edit','channel_type']:                
                order_column = getattr(Channel, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)
            
            result = await session.execute(query)
            channels = result.scalars().all()
            for channel in channels:
                files_result = await session.execute(select(File).filter(File.assistant_id == channel.id))
                files = [file.name for file in files_result.scalars()]
                channel.files = files

            channels = [ChannelSchema.from_orm(channel) for channel in channels] 
            
            # Get total count
            count_query = select(func.count()).select_from(Channel)
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        count_query = count_query.filter(Channel.name.ilike(f"%{value}%"))
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(Channel, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Channel, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return channels, total_count


    async def create_file(self, file_name: str, assistant_id: str ) -> str:        
        async with db_session_context() as session:
            new_file = File(id=str(uuid4()), name=file_name, assistant_id=assistant_id)
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)
            return new_file.id
        
    async def update_file(self, assistant_id: str, file_name: str) -> str:
        async with db_session_context() as session:
            # delete the file from the database if it exists
            stmt = delete(File).where(File.assistant_id == assistant_id)
            await session.execute(stmt)
            await session.commit()
            return self.create_file(file_name, assistant_id)

    def validate_channel_data(self, channel_data: ChannelCreateSchema ) -> str:
        if not channel_data["status"] in ["public", "private","draft"]:
            return "Not a valid status"
        if not channel_data["allow_edit"] in ["True", "False"]:
            return "Not a valid allow_edit"
        if not channel_data["channel_type"] in ["llm", "assistant"]:
            return "Not a valid channel_type"
        return None