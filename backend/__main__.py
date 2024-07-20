import sys
import signal
import asyncio
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))
from backend.env import check_env
from common.paths import backend_dir, venv_dir

# set up logging
from common.log import get_logger
logger = get_logger(__name__)

def handle_shutdown(signum, frame):
    print(f"Shutdown signal received (ID: {signum}). Cleaning up...")
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.stop()
    except RuntimeError:
        logger.info("No running event loop found during shutdown.")

def cleanup():
    logger.info("Performing cleanup tasks.")
    try:
        # Get the current event loop using the new method
        loop = asyncio.get_running_loop()
        
        # Cancel all tasks
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        
        # Run the event loop one last time to execute the cancellations
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        
        # Close the loop
        loop.close()
    except RuntimeError:
        logger.info("No running event loop found. Skipping task cancellation.")

def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Check if the environment is set up and activated before importing dependencies
    check_env()

    # Create the app
    from app import create_app
    app = create_app()

    # Run the app
    import uvicorn

    logger.info("Running the app with uvicorn.")
    try:
        uvicorn.run("app:create_app", host="localhost", port=3080, factory=True, workers=1, reload=True, reload_dirs=[backend_dir], reload_excludes=[venv_dir])
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
