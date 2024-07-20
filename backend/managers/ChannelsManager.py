from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Channel
from backend.db import db_session_context

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
                    self._initialized = True

    async def create_channel(self, name, uri):
        async with db_session_context() as session:
            new_channel = Channel(id=str(uuid4()), name=name, uri=uri)
            session.add(new_channel)
            await session.commit()
            return new_channel.id

    async def update_channel(self, id, name, uri):
        async with db_session_context() as session:
            stmt = update(Channel).where(Channel.id == id).values(name=name, uri=uri)
            await session.execute(stmt)
            await session.commit()

    async def delete_channel(self, id):
        async with db_session_context() as session:
            stmt = delete(Channel).where(Channel.id == id)
            await session.execute(stmt)
            await session.commit()

    async def retrieve_channel(self, id):
        async with db_session_context() as session:
            result = await session.execute(select(Channel).filter(Channel.id == id))
            channel = result.scalar_one_or_none()
            return channel.to_dict() if channel else None

    async def retrieve_channels(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None):
        async with db_session_context() as session:
            query = select(Channel)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.filter(getattr(Channel, key).in_(value))
                    else:
                        query = query.filter(getattr(Channel, key) == value)

            if sort_by and sort_by in ['id', 'name', 'uri']:
                order_column = getattr(Channel, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            channels = [channel.to_dict() for channel in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(Channel)
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(Channel, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Channel, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return channels, total_count
