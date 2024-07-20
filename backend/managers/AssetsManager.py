from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func, or_
from backend.models import Asset
from backend.db import db_session_context
from backend.utils import remove_null_fields

class AssetsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AssetsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True

    async def create_asset(self, user_id, title, creator, subject, description):
        async with db_session_context() as session:
            new_asset = Asset(id=str(uuid4()), user_id=user_id, title=title, creator=creator, subject=subject, description=description)
            session.add(new_asset)
            await session.commit()
            return new_asset.id

    async def update_asset(self, id, user_id, title, creator, subject, description):
        async with db_session_context() as session:
            stmt = update(Asset).where(Asset.id == id).values(user_id=user_id, title=title, creator=creator, subject=subject, description=description)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def delete_asset(self, id):
        async with db_session_context() as session:
            stmt = delete(Asset).where(Asset.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_asset(self, id):
        async with db_session_context() as session:
            result = await session.execute(select(Asset).filter(Asset.id == id))
            asset = result.scalar_one_or_none()
            return remove_null_fields(asset.to_dict()) if asset else None

    async def retrieve_assets(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None, query=None):
        async with db_session_context() as session:
            stmt = select(Asset)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        stmt = stmt.filter(getattr(Asset, key).in_(value))
                    else:
                        stmt = stmt.filter(getattr(Asset, key) == value)

            if query:
                search_condition = or_(
                    Asset.title.ilike(f"%{query}%"),
                    Asset.description.ilike(f"%{query}%"),
                    Asset.creator.ilike(f"%{query}%"),
                    Asset.subject.ilike(f"%{query}%")
                )
                stmt = stmt.filter(search_condition)

            if sort_by and hasattr(Asset, sort_by):
                order_column = getattr(Asset, sort_by)
                stmt = stmt.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            stmt = stmt.offset(offset).limit(limit)

            result = await session.execute(stmt)
            assets = [remove_null_fields(asset.to_dict()) for asset in result.scalars().all()]

            # Get total count
            count_stmt = select(func.count()).select_from(Asset)
            if filters or query:
                count_stmt = count_stmt.filter(stmt.whereclause)
            total_count = await session.execute(count_stmt)
            total_count = total_count.scalar()

            return assets, total_count