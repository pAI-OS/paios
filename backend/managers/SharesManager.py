import secrets
import string
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Share
from backend.db import db_session_context
from backend.schemas import ShareCreateSchema, ShareSchema
from typing import List, Tuple, Optional, Dict, Any

def generate_share_id():
    # SHARE_ID_REGEX = '[a-z]{3}-[a-z]{3}-[a-z]{3}'
    return '-'.join(''.join(secrets.choice(string.ascii_lowercase) for _ in range(3)) for _ in range(3))

class SharesManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SharesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    # db.init_db()
                    self._initialized = True

    async def create_share(self, resource_id, user_id, expiration_dt, is_revoked=False) -> ShareSchema:
        async with db_session_context() as session:
            new_key = None
            while not new_key:
                new_key = generate_share_id()
                result = await session.execute(select(Share).filter(Share.id == new_key))
                share = result.scalar_one_or_none()
                if share:  # new_key already in use
                    new_key = None
            new_share = Share(id=new_key, resource_id=resource_id, user_id=user_id,
                              expiration_dt=expiration_dt, is_revoked=is_revoked)
            session.add(new_share)
            await session.commit()
            await session.refresh(new_share)
            return ShareSchema(id=new_share.id, resource_id=new_share.resource_id,
                               user_id=new_share.user_id, expiration_dt=new_share.expiration_dt,
                               is_revoked=new_share.is_revoked)

    async def update_share(self, id: str, resource_id, user_id, expiration_dt, is_revoked) -> Optional[ShareSchema]:
        async with db_session_context() as session:
            stmt = update(Share).where(Share.id == id).values(resource_id=resource_id,
                                                                user_id=user_id,
                                                                expiration_dt=expiration_dt,
                                                                is_revoked=is_revoked)
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_share = await session.get(Share, id)
                return ShareSchema(id=updated_share.id, resource_id=updated_share.resource_id,
                               user_id=updated_share.user_id, expiration_dt=updated_share.expiration_dt,
                               is_revoked=updated_share.is_revoked)
            return None

    async def delete_share(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Share).where(Share.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_share(self, id: str) -> Optional[ShareSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Share).filter(Share.id == id))
            share = result.scalar_one_or_none()
            if share:
                return ShareSchema(id=share.id, resource_id=share.resource_id, user_id=share.user_id,
                                   expiration_dt=share.expiration_dt, is_revoked=share.is_revoked)
            return None

    async def retrieve_shares(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                              sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[ShareSchema], int]:
        async with db_session_context() as session:
            query = select(Share)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.filter(getattr(Share, key).in_(value))
                    else:
                        query = query.filter(getattr(Share, key) == value)

            if sort_by and sort_by in ['id', 'resource_id', 'user_id', 'expiration_dt', 'is_revoked']:
                order_column = getattr(Share, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            shares = [ShareSchema(id=share.id, resource_id=share.resource_id, user_id=share.user_id,
                                  expiration_dt=share.expiration_dt, is_revoked=share.is_revoked) 
                        for share in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(Share)
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(Share, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Share, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return shares, total_count
