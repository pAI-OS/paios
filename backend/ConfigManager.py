import os
import sqlite3
from pathlib import Path
from alembic import command
from alembic.config import Config as AlembicConfig
from EncryptionManager import EncryptionManager
from paths import root_dir, db_path

class ConfigManager:
    def __init__(self, tenant=None):
        self.em = EncryptionManager()
        self.tenant = tenant
        #self.backend_path = Path(__file__).resolve().parent
        #self.base_path = self.backend_path.parent
        #self.db_path = self.base_path / 'data' / (self.tenant if self.tenant else '')
        #self.db_path = self.db_path / 'paios.db'
        os.makedirs(db_path.parent, exist_ok=True)

        # use alembic to create the database or migrate to the latest schema
        self.init_db()

    def init_db(self):
        alembic_cfg = AlembicConfig()
        alembic_cfg.set_main_option("script_location", str(root_dir / "migrations"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
        command.upgrade(alembic_cfg, "head")

    def execute_query(self, query, params=None):
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

    # CRUD operations
    def create_config_item(self, key, value):
        encrypted_value = self.em.encrypt_value(value)
        query = 'INSERT INTO config (key, value) VALUES (?, ?)'
        self.execute_query(query, (key, encrypted_value))

    def retrieve_config_item(self, key):
        query = 'SELECT value FROM config WHERE key = ?'
        result = self.execute_query(query, (key,))
        if result:
            encrypted_value = result[0][0]
            return self.em.decrypt_value(encrypted_value)
        return None

    def update_config_item(self, key, value):
        encrypted_value = self.em.encrypt_value(value)
        query = 'INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)'
        self.execute_query(query, (key, encrypted_value))

    def delete_config_item(self, key):
        query = 'DELETE FROM config WHERE key = ?'
        self.execute_query(query, (key,))
