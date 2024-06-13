import os
import json
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
from common.paths import base_dir
class Encryption:
    _instance = None

    # Singleton pattern so we only read from .env once for the life of the application
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Encryption, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, encryption_key=None):
        if self._initialized:
            return
        self._initialized = True
        load_dotenv(base_dir / '.env')
        self.encryption_key = encryption_key if encryption_key else self.get_encryption_key()

    # Helper function to get the encryption key from environment variables or generate a new one and save it to .env
    def get_encryption_key(self):
        encryption_key = os.environ.get('PAIOS_DB_ENCRYPTION_KEY')
        if not encryption_key:
            encryption_key = Fernet.generate_key().decode()
            set_key(base_dir / '.env', 'PAIOS_DB_ENCRYPTION_KEY', encryption_key)
        return encryption_key

    # Encrypt a value using Fernet encryption
    def encrypt_value(self, value):
        f = Fernet(self.encryption_key)
        if type(value) in (dict, list):
           value = json.dumps(value)
        encrypted_value = f.encrypt(value.encode())
        return encrypted_value

    # Decrypt a value using Fernet encryption
    def decrypt_value(self, encrypted_value):
        f = Fernet(self.encryption_key)
        decrypted_value = f.decrypt(encrypted_value).decode()
        return decrypted_value
