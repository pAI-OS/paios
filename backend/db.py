# database helper functions
import os
import logging
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config as AlembicConfig
from common.paths import base_dir, db_path, db_url
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Define SQLModelBase class
class SQLModelBase(SQLModel):
    pass

# Create async engine
engine = create_async_engine(db_url, echo=False)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# use alembic to create the database or migrate to the latest schema
def init_db():
    logger.info("Initializing database.")
    alembic_cfg = AlembicConfig()
    os.makedirs(db_path.parent, exist_ok=True)
    alembic_cfg.set_main_option("script_location", str(base_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url.replace("+aiosqlite", "")) # because Alembic doesn't like async apparently
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def db_session_context():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
