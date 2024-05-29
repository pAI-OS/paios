import os
import secrets
from starlette.requests import Request
from starlette.responses import JSONResponse
from dotenv import load_dotenv, set_key

# Load the environment variables from the .env file
load_dotenv()

# Check if PAIOS_BEARER_TOKEN is set; if not, create one and set_key it to .env
if not os.getenv('PAIOS_BEARER_TOKEN'):
    token = secrets.token_hex(32)
    os.environ['PAIOS_BEARER_TOKEN'] = token
    set_key('.env', 'PAIOS_BEARER_TOKEN', token)

    # Set the token to the frontend/.env file as well so the frontend can use it
    env_file = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env')
    set_key(env_file, 'VITE_PAIOS_BEARER_TOKEN', token)

def validate_bearer_token(request: Request):
    if request.method == 'OPTIONS':
        return  # Allow OPTIONS requests to pass through without a token

    token = request.headers.get('Authorization')
    if not token:
        return JSONResponse({'error': 'Missing token'}, status_code=401)
    if token.split(" ")[1] != os.environ['PAIOS_BEARER_TOKEN']:
        return JSONResponse({'error': 'Invalid token'}, status_code=403)
