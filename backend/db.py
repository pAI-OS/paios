# database helper functions
import os
import sqlite3
from alembic import command
from alembic.config import Config as AlembicConfig
from paths import root_dir, db_path

# use alembic to create the database or migrate to the latest schema
def init_db():
    alembic_cfg = AlembicConfig()
    os.makedirs(db_path.parent, exist_ok=True)
    alembic_cfg.set_main_option("script_location", str(root_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

def execute_query(query, params=None):
    print(f"Executing query: {query} with params: {params}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return result
