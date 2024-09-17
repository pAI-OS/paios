from pathlib import Path
from backend.app import create_backend_app
from starlette.staticfiles import StaticFiles
from backend.redirector import redirector

# set up logging
from common.log import get_logger
logger = get_logger(__name__)

def create_app():
    app = create_backend_app()
    add_redirector_app(app)
    add_frontend_app(app)
    return app

def add_frontend_app(app):
    # Add a route for serving static files if the frontend dist directory exists
    static_dir = Path(__file__).parent / 'frontend' / 'dist'
    if static_dir.is_dir():
        # Add a route for serving static files only if the directory exists
        app.add_url_rule(
            '/{path:path}', 
            endpoint='frontend', 
            view_func=StaticFiles(directory=static_dir, check_dir=False, html=True)
        )
    else:
        logger.info(f"Skipping serving frontend: {static_dir} directory not found. Options:")
        logger.info("- Use 'npm run build' to generate the frontend")
        logger.info("- Use 'npm run dev' to run it separately")
        logger.info("- Use the API only")

def add_redirector_app(app):
    # Add a route for handling URL redirection for bot access
    app.add_url_rule(
        '/r/{url_key:str}', 
        endpoint='redirector',
        view_func=redirector
    )

