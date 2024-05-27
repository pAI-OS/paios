import connexion
from connexion.resolver import MethodResolver
from pathlib import Path

def create_backend_app():
    apis_dir = Path(__file__).parent.parent / 'apis' / 'paios'
    connexion_app = connexion.AsyncApp(__name__, specification_dir=apis_dir)

    # Connexion API resolver allows for:
    #  - python -m paios
    #  - python -m backend
    #  - python __main__.py
    if __package__ == 'paios.backend':
        api_resolver = 'paios.backend.api'
    elif __package__ == 'backend':
        api_resolver = 'backend.api'
    else:
        api_resolver = 'api'
    print("api_resolver: ", api_resolver)

    connexion_app.add_api('openapi.yaml', resolver=MethodResolver(api_resolver), resolver_error=501)

    return connexion_app

if __name__ == '__main__':
    import uvicorn
    try:
        uvicorn.run("__main__:create_backend_app", host="localhost", port=3080, factory=True, workers=1)
    except KeyboardInterrupt:
        print("Server stopped")
