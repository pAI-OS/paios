from pathlib import Path
from starlette.staticfiles import StaticFiles

# Conditional import based on the running context (module or script)
try:
    from paios.backend.__main__ import create_backend_app
except ImportError:
    from backend.__main__ import create_backend_app

def create_app():
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
    import uvicorn
    uvicorn.run("__main__:create_app", host="localhost", port=3080, factory=True, workers=1)
