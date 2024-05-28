import sys
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent.parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))

def create_backend_app():
    import connexion
    from connexion.resolver import MethodResolver
    from pathlib import Path

    apis_dir = Path(__file__).parent.parent / 'apis' / 'paios'
    connexion_app = connexion.AsyncApp(__name__, specification_dir=apis_dir)

    connexion_app.add_api('openapi.yaml', resolver=MethodResolver('backend.api'), resolver_error=501)

    return connexion_app

if __name__ == '__main__':
    from backend.env import check_env
    check_env()

    import uvicorn
    try:
        uvicorn.run("__main__:create_backend_app", host="localhost", port=3080, factory=True, workers=1)
    except KeyboardInterrupt:
        print("Server stopped")
