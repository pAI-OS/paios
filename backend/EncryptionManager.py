import os
import json
from dotenv import set_key
from cryptography.fernet import Fernet

class EncryptionManager:
    def __init__(self, encryption_key=None):
        self.encryption_key = encryption_key if encryption_key else self.get_encryption_key()

    # Helper function to get the encryption key from environment variables or generate a new one and save it to .env
    def get_encryption_key(self):
        encryption_key = os.environ.get('PAIOS_DB_ENCRYPTION_KEY')
        if not encryption_key:
            encryption_key = Fernet.generate_key().decode()
            set_key('.env', 'PAIOS_DB_ENCRYPTION_KEY', encryption_key)
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
