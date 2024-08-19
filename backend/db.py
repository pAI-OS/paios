# database helper functions
import os
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from alembic import command
from alembic.config import Config as AlembicConfig
from common.paths import base_dir, db_path, db_url
from contextlib import asynccontextmanager

# Define the SQLAlchemy Base
Base = declarative_base()

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
