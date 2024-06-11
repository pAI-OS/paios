import sys
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))
from backend.env import check_env
from backend.paths import backend_dir, venv_dir, log_db_path
from backend.log import logger

logger.info("Starting server...")

if __name__ == "__main__":
    # Check if the environment is set up and activated before importing dependencies
    check_env()
    from starlette.staticfiles import StaticFiles

    # Create the app
    from app import create_app
    app = create_app()

    # Run the app
    import uvicorn
    uvicorn.run("app:create_app", host="localhost", port=3080, factory=True, workers=1, reload=True, reload_dirs=[backend_dir], reload_excludes=[venv_dir])
