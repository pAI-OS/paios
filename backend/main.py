#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent.parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))

from backend.env import check_env

def create_app():
    import connexion
    from flask_cors import CORS
    from auth import validate_bearer_token

    # Uses the connexion library to create a Flask app implmenting the OpenAPI
    # specification (../apis/paios/openapi.yaml), calling the python functions
    # in operationId (eg api.get_asset_by_id in api.py)

    app = connexion.App(__name__, specification_dir='../apis/paios/')
    CORS(app.app, origins='http://localhost:5173', expose_headers='X-Total-Count', supports_credentials=True)

    app.app.before_request(validate_bearer_token)

    app.add_api('openapi.yaml')

    return app

if __name__ == '__main__':
    #check_env()

    app = create_app()
    app.run(host='localhost', port=3080)
