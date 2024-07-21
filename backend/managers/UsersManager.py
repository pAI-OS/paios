from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import User
from backend.db import db_session_context
from backend.schemas import UserSchema

class UsersManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UsersManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    # db.init_db()
                    self._initialized = True

    async def create_user(self, name, email):
        async with db_session_context() as session:
            new_user = User(id=str(uuid4()), name=name, email=email)
            session.add(new_user)
            await session.commit()
            return new_user.id

    async def update_user(self, id, name, email):
        async with db_session_context() as session:
            stmt = update(User).where(User.id == id).values(name=name, email=email)
            await session.execute(stmt)
            await session.commit()

    async def delete_user(self, id):
        async with db_session_context() as session:
            stmt = delete(User).where(User.id == id)
            await session.execute(stmt)
            await session.commit()

    async def retrieve_user(self, id):
        async with db_session_context() as session:
            result = await session.execute(select(User).filter(User.id == id))
            user = result.scalar_one_or_none()
            return UserSchema(id=user.id, name=user.name, email=user.email) if user else None

    async def retrieve_users(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None):
        async with db_session_context() as session:
            query = select(User)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.filter(getattr(User, key).in_(value))
                    else:
                        query = query.filter(getattr(User, key) == value)

            if sort_by and sort_by in ['id', 'name', 'email']:
                order_column = getattr(User, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            users = [UserSchema(
                id=user.id,
                name=user.name,
                email=user.email
            ) for user in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(User)
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(User, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(User, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return users, total_count