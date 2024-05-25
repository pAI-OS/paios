#!/usr/bin/env python3
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
    import os
    import sys

    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Running in a virtual environment ({})".format(sys.prefix))
    else:
        print("Erorr: Running under the system python ({})\n".format(sys.prefix))
        print("Please create a virtual environment, install the dependencies, and activate it before running this again.\n")
        if os.name == "posix": # Linux, macOS, etc.
            print("You can use the scripts/setup_environment.sh script to do this, or do it manually:")
            print("    python3 -m venv .venv")
            print("    source .venv/bin/activate")
            print("    pip install -r backend/requirements.txt")
        elif os.name == "nt": # Windows
            print("You can use the scripts\\setup_environment.ps1 script to do this, or do it manually from the root directory:\n")
            print("    python -m venv .venv")
            print("    .venv\\Scripts\\activate")
            print("    pip install -r backend\\requirements.txt\n")
        sys.exit(1)

    required_modules = ['connexion', 'flask_cors']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"Required module {module} is not installed.")
            sys.exit(1)

    app = create_app()
    app.run(host='localhost', port=3080)
