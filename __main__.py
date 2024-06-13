import asyncio
import sys
import signal
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))
from backend.env import check_env
from common.paths import backend_dir, venv_dir
from common.config import logging_config

# set up logging
from common.log import get_logger
logger = get_logger(__name__)

def handle_keyboard_interrupt(signum, frame):
    print("Cleaning up...")
    cleanup()
    asyncio.get_event_loop().stop()

def cleanup():
    # Perform any necessary cleanup here
    logger.info("Performing cleanup tasks...")

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_keyboard_interrupt)
    signal.signal(signal.SIGTERM, handle_keyboard_interrupt)

    logger.info(f"Checking if the environment in {venv_dir} is set up and activated before importing dependencies.", extra={'x': 'y'})
    check_env()

    # Create the app
    logger.info("Creating the app...")
    from app import create_app
    app = create_app()

    # Run the app
    import uvicorn
    
    logger.info("Running the app...")
    try:
        logger.info(f"Logging config: {logging_config}")
        uvicorn.run("app:create_app", host="localhost", port=3080, factory=True, workers=1, reload=True, reload_dirs=[backend_dir], reload_excludes=[venv_dir], log_config=logging_config)
    except KeyboardInterrupt:
        handle_keyboard_interrupt(None, None)
    finally:
        cleanup()
