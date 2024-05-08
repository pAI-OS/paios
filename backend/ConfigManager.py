import db
from EncryptionManager import EncryptionManager
from paths import db_path

class ConfigManager:
    def __init__(self, tenant=None):
        self.em = EncryptionManager()
        self.tenant = tenant
        db.init_db()

    # CRUD operations
    def create_config_item(self, key, value):
        encrypted_value = self.em.encrypt_value(value)
        query = 'INSERT INTO config (key, value) VALUES (?, ?)'
        db.execute_query(query, (key, encrypted_value))

    def retrieve_config_item(self, key):
        query = 'SELECT value FROM config WHERE key = ?'
        result = db.execute_query(query, (key,))
        if result:
            encrypted_value = result[0][0]
            return self.em.decrypt_value(encrypted_value)
        return None

    def update_config_item(self, key, value):
        encrypted_value = self.em.encrypt_value(value)
        query = 'INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)'
        db.execute_query(query, (key, encrypted_value))

    def delete_config_item(self, key):
        query = 'DELETE FROM config WHERE key = ?'
        db.execute_query(query, (key,))
