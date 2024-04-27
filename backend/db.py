import os
import sqlite3
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file including the encryption key if not already set
load_dotenv()

# Helper function to connect, execute, commit, and close the database
def execute_query(query, params=None, tenant=None):
    db_path = os.path.join('..', 'data', tenant, 'config.db') if tenant else os.path.join('..', 'data', 'config.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Create the path if required

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create the table if it doesn't exist
        cursor.execute("CREATE TABLE config (key TEXT UNIQUE, value TEXT)")
        cursor.execute("CREATE INDEX idx_config_key ON config (key)")

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return result

# Helper function to get the encryption key from environment variables or generate a new one and save it to .env
def get_encryption_key():
    encryption_key = os.environ.get('PAIOS_DB_ENCRYPTION_KEY')
    if not encryption_key:
        encryption_key = Fernet.generate_key().decode()
        with open('.env', 'a') as f:
            f.write(f'PAIOS_DB_ENCRYPTION_KEY={encryption_key}\n')
    return encryption_key

# Encrypt a value using Fernet encryption
def encrypt_value(value):
    f = Fernet(get_encryption_key())
    encrypted_value = f.encrypt(value.encode())
    return encrypted_value

# Decrypt a value using Fernet encryption
def decrypt_value(encrypted_value):
    f = Fernet(get_encryption_key())
    decrypted_value = f.decrypt(encrypted_value).decode()
    return decrypted_value

# Create a new config item
def create_config_item(key, value, tenant=None):
    encrypted_value = encrypt_value(value)
    query = 'INSERT INTO config (key, value) VALUES (?, ?)'
    execute_query(query, (key, encrypted_value), tenant)

# Read a config item by key
def read_config_item(key, tenant=None):
    query = 'SELECT value FROM config WHERE key = ?'
    result = execute_query(query, (key,), tenant)
    if result:
        encrypted_value = result[0][0]
        decrypted_value = decrypt_value(encrypted_value)
        return decrypted_value
    else:
        return None

# Update a config item by key
def update_config_item(key, value, tenant=None):
    encrypted_value = encrypt_value(value)
    query = 'UPDATE config SET value = ? WHERE key = ?'
    execute_query(query, (encrypted_value, key), tenant)

# Delete a config item by key
def delete_config_item(key, tenant=None):
    query = 'DELETE FROM config WHERE key = ?'
    execute_query(query, (key,), tenant)
