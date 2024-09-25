# backend/managers/ConfigManager.py

from uuid import uuid4
from threading import Lock
from datetime import datetime
from sqlalchemy import select, update, delete, func
from backend.models import Config
from backend.db import db_session_context
from backend.encryption import Encryption
from backend.schemas import ConfigSchema

class ConfigManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, tenant=None):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self.encryption = Encryption()
                    self.tenant = tenant
                    self._initialized = True

    async def create_config_item(self, key, value, version=None, environment_id=None, user_id=None):
        async with db_session_context() as session:
            # Get the latest version number for the key, environment_id, and user_id
            result = await session.execute(
                select(func.max(Config.version)).filter(
                    Config.key == key,
                    #Config.environment_id == environment_id,
                    Config.user_id == user_id
                )
            )
            latest_version = result.scalar() or 0
            new_version = latest_version + 1

            id = str(uuid4())
            encrypted_value = self.encryption.encrypt_value(value)
            new_config = Config(
                id=id,
                key=key,
                value=encrypted_value,
                version=new_version,
                #environment_id=environment_id,
                user_id=user_id,
                created_at=None,
                updated_at=None,
            )
            session.add(new_config)
            await session.commit()
        return ConfigSchema(
            id=id,
            key=key,
            value=value,
            version=new_version,
            #environment_id=environment_id,
            user_id=user_id,
            created_at=new_config.created_at,
            updated_at=new_config.updated_at,
        )

    async def retrieve_config_item(self, key, version=None, environment_id=None, user_id=None):
        async with db_session_context() as session:
            query = select(Config).filter(
                Config.key == key,
                Config.environment_id == environment_id,
                Config.user_id == user_id
            )
            if version:
                query = query.filter(Config.version == version)
            else:
                query = query.order_by(Config.version.desc()).limit(1)
            result = await session.execute(query)
            config = result.scalar_one_or_none()
            if config:
                decrypted_value = self.encryption.decrypt_value(config.value)
                return ConfigSchema(
                    id=config.id,
                    key=config.key,
                    value=decrypted_value,
                    version=config.version,
                    #environment_id=config.environment_id,
                    user_id=config.user_id,
                    created_at=config.created_at,
                    updated_at=config.updated_at,
                )
        return None

    async def update_config_item(self, key, value, version=None, environment_id=None, user_id=None):
        async with db_session_context() as session:
            # Get the latest version number for the key, environment_id, and user_id
            result = await session.execute(
                select(func.max(Config.version)).filter(
                    Config.key == key,
                    #Config.environment_id == environment_id,
                    Config.user_id == user_id
                )
            )
            latest_version = result.scalar() or 0
            new_version = latest_version + 1

            id = str(uuid4())
            encrypted_value = self.encryption.encrypt_value(value)
            new_config = Config(
                id=id,
                key=key,
                value=encrypted_value,
                version=new_version,
                #environment_id=environment_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(new_config)
            await session.commit()
        return ConfigSchema(
            id=id,
            key=key,
            value=value,
            version=new_version,
            #environment_id=environment_id,
            user_id=user_id,
            created_at=new_config.created_at,
            updated_at=new_config.updated_at,
        )

    async def delete_config_item(self, key, version=None, environment_id=None, user_id=None):
        async with db_session_context() as session:
            query = delete(Config).filter(
                Config.key == key,
                #Config.environment_id == environment_id,
                Config.user_id == user_id
            )
            if version:
                query = query.filter(Config.version == version)
            result = await session.execute(query)
            await session.commit()
        return result.rowcount > 0

    async def retrieve_all_config_items(self, filters=None):
        filters = filters or {}
        async with db_session_context() as session:
            query = select(Config)
            for key, value in filters.items():
                query = query.filter(getattr(Config, key) == value)
            result = await session.execute(query)
            configs = result.scalars().all()
            return [
                ConfigSchema(
                    id=config.id,
                    key=config.key,
                    value=self.encryption.decrypt_value(config.value),
                    version=config.version,
                    #environment_id=config.environment_id,
                    user_id=config.user_id,
                    created_at=config.created_at,
                    updated_at=config.updated_at,
                )
                for config in configs
            ]
