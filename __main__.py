import sys
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))

# Requires sys.path to be set first
from backend.env import check_env

# Conditional import based on the running context (module or script)
#try:
#    from paios.backend.__main__ import create_backend_app
#except ImportError:
#from paios.backend.__main__ import create_backend_app

def create_app():
    from backend.__main__ import create_backend_app
    app = create_backend_app()


    # Add a route for serving static files
    static_dir = Path(__file__).parent / 'frontend' / 'dist'
    app.add_url_rule(
        '/{path:path}', 
        endpoint='frontend', 
        view_func=StaticFiles(directory=static_dir, html=True)
    )

    return app

if __name__ == "__main__":
    # Check if the environment is set up and activated before importing dependencies
    check_env()
    from starlette.staticfiles import StaticFiles

    # Create the app
    app = create_app()

    # Run the app
    import uvicorn
    uvicorn.run("__main__:create_app", host="localhost", port=3080, factory=True, workers=1)
