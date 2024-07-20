from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func, or_
from backend.models import Asset
from backend.db import db_session_context
from backend.schemas import AssetSchema, AssetCreateSchema
from typing import List, Tuple, Optional, Dict, Any

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

    async def create_asset(self, asset_data: AssetCreateSchema) -> AssetSchema:
        async with db_session_context() as session:
            new_asset = Asset(id=str(uuid4()), **asset_data.model_dump())
            session.add(new_asset)
            await session.commit()
            await session.refresh(new_asset)
            return AssetSchema(id=new_asset.id, **asset_data.model_dump())

    async def update_asset(self, id: str, asset_data: AssetCreateSchema) -> Optional[AssetSchema]:
        async with db_session_context() as session:
            stmt = update(Asset).where(Asset.id == id).values(**asset_data.model_dump(exclude_unset=True))
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_asset = await session.get(Asset, id)
                return AssetSchema(id=updated_asset.id, **asset_data.model_dump())
            return None

    async def delete_asset(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Asset).where(Asset.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_asset(self, id: str) -> Optional[AssetSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Asset).filter(Asset.id == id))
            asset = result.scalar_one_or_none()
            if asset:
                return AssetSchema(
                    id=asset.id,
                    title=asset.title,
                    user_id=asset.user_id,
                    creator=asset.creator,
                    subject=asset.subject,
                    description=asset.description
                )
            return None

    async def retrieve_assets(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                              sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None, 
                              query: Optional[str] = None) -> Tuple[List[AssetSchema], int]:
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
            assets = [AssetSchema(
                id=asset.id,
                title=asset.title,
                user_id=asset.user_id,
                creator=asset.creator,
                subject=asset.subject,
                description=asset.description
            ) for asset in result.scalars().all()]

            # Get total count
            count_stmt = select(func.count()).select_from(Asset)
            if filters or query:
                count_stmt = count_stmt.filter(stmt.whereclause)
            total_count = await session.execute(count_stmt)
            total_count = total_count.scalar()

            return assets, total_count
