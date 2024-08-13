from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Resource
from backend.db import db_session_context
from backend.schemas import ChannelCreateSchema, ChannelSchema
from typing import List, Tuple, Optional, Dict, Any

class ResourcesManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ResourcesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    # db.init_db()
                    self._initialized = True

    async def create_resource(self, resource_data: ChannelCreateSchema) -> ChannelSchema:
        async with db_session_context() as session:
            new_resource = Resource(id=str(uuid4()), **resource_data.model_dump())
            session.add(new_resource)
            await session.commit()
            await session.refresh(new_resource)
            return ChannelSchema(id=new_resource.id, **resource_data.model_dump())

    async def update_resource(self, id: str, resource_data: ChannelCreateSchema) -> Optional[ChannelSchema]:
        async with db_session_context() as session:
            stmt = update(Resource).where(Resource.id == id).values(**resource_data.dict())
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_resource = await session.get(Resource, id)
                return ChannelSchema(id=updated_resource.id, **resource_data.model_dump())
            return None

    async def delete_resource(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Resource).where(Resource.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_resource(self, id: str) -> Optional[ChannelSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Resource).filter(Resource.id == id))
            resource = result.scalar_one_or_none()
            if resource:
                return ChannelSchema(id=resource.id, name=resource.name, uri=resource.uri)
            return None

    async def retrieve_resources(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                                sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[ChannelSchema], int]:
        async with db_session_context() as session:
            query = select(Resource)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.filter(getattr(Resource, key).in_(value))
                    else:
                        query = query.filter(getattr(Resource, key) == value)

            if sort_by and sort_by in ['id', 'name', 'uri']:
                order_column = getattr(Resource, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            resources = [ChannelSchema(id=resource.id, name=resource.name, uri=resource.uri) 
                        for resource in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(Resource)
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(Resource, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Resource, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return resources, total_count
