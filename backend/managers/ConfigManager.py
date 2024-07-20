from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete
from backend.models import Config
from backend.db import db_session_context, init_db
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
                    init_db()
                    self._initialized = True

    async def create_config_item(self, value):
        key = str(uuid4())
        encrypted_value = self.encryption.encrypt_value(value)
        async with db_session_context() as session:
            new_config = Config(key=key, value=encrypted_value)
            session.add(new_config)
            await session.commit()
        return ConfigSchema(key=key, value=value)

    async def retrieve_config_item(self, key):
        async with db_session_context() as session:
            result = await session.execute(select(Config).filter(Config.key == key))
            config = result.scalar_one_or_none()
            if config:
                decrypted_value = self.encryption.decrypt_value(config.value)
                return ConfigSchema(key=config.key, value=decrypted_value)
        return None

    async def update_config_item(self, key, value):
        encrypted_value = self.encryption.encrypt_value(value)
        async with db_session_context() as session:
            stmt = update(Config).where(Config.key == key).values(value=encrypted_value)
            result = await session.execute(stmt)
            if result.rowcount == 0:
                new_config = Config(key=key, value=encrypted_value)
                session.add(new_config)
            await session.commit()
        return ConfigSchema(key=key, value=value)

    async def delete_config_item(self, key):
        async with db_session_context() as session:
            stmt = delete(Config).where(Config.key == key)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount > 0

    async def retrieve_all_config_items(self):
        async with db_session_context() as session:
            result = await session.execute(select(Config))
            configs = result.scalars().all()
            return [ConfigSchema(key=config.key, value=self.encryption.decrypt_value(config.value)) 
                    for config in configs]