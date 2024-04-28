import os
import secrets
from flask import request, jsonify
from dotenv import load_dotenv, set_key

# Load the environment variables from the .env file
load_dotenv()

# Check if PAIOS_BEARER_TOKEN is set; if not, create one and set_key it to .env
if not os.getenv('PAIOS_BEARER_TOKEN'):
    token = secrets.token_hex(32)
    set_key('.env', 'PAIOS_BEARER_TOKEN', token)
    
    # Set the token to the admin/.env file as well so the admin app can use it
    env_file = os.path.join(os.path.dirname(__file__), '..', 'admin', '.env')
    set_key(env_file, 'PAIOS_BEARER_TOKEN', token)

def validate_bearer_token():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    if token.split(" ")[1] != 'valid_token':  # Replace 'valid_token' with your actual token validation logic
        return jsonify({'error': 'Invalid token'}), 403
