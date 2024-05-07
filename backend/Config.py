import os
import sqlite3
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
from alembic import command
from alembic.config import Config as AlembicConfig

class Config:
    def __init__(self, tenant=None):
        load_dotenv()
        self.tenant = tenant
        self.db_path = os.path.join('..', 'data', self.tenant, 'config.db') if self.tenant else os.path.join('..', 'data', 'config.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.encryption_key = self.get_encryption_key()
        self.init_db()

    def init_db(self):
        alembic_cfg = AlembicConfig("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{self.db_path}")
        command.upgrade(alembic_cfg, "head")

    def execute_query(self, query, params=None):
        conn = sqlite3.connect(self.db_path)
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

    def get_encryption_key(self):
        encryption_key = os.environ.get('PAIOS_DB_ENCRYPTION_KEY')
        if not encryption_key:
            encryption_key = Fernet.generate_key().decode()
            set_key('.env', 'PAIOS_DB_ENCRYPTION_KEY', encryption_key)
        return encryption_key

    def encrypt_value(self, value):
        f = Fernet(self.encryption_key)
        return f.encrypt(value.encode())

    def decrypt_value(self, encrypted_value):
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_value).decode()

    def set_config_item(self, key, value):
        encrypted_value = self.encrypt_value(value)
        query = 'INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)'
        self.execute_query(query, (key, encrypted_value))

    def create_config_item(self, key, value):
        encrypted_value = self.encrypt_value(value)
        query = 'INSERT INTO config (key, value) VALUES (?, ?)'
        self.execute_query(query, (key, encrypted_value))

    def read_config_item(self, key):
        query = 'SELECT value FROM config WHERE key = ?'
        result = self.execute_query(query, (key,))
        if result:
            encrypted_value = result[0][0]
            return self.decrypt_value(encrypted_value)
        return None

    def update_config_item(self, key, value):
        encrypted_value = self.encrypt_value(value)
        query = 'UPDATE config SET value = ? WHERE key = ?'
        self.execute_query(query, (encrypted_value, key))

    def delete_config_item(self, key):
        query = 'DELETE FROM config WHERE key = ?'
        self.execute_query(query, (key,))
