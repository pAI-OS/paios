import sys
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent.parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))

if __name__ == '__main__':
    from backend.env import check_env
    check_env()

    from backend.app import create_backend_app

    import uvicorn
    try:
        uvicorn.run("app:create_backend_app", host="localhost", port=3080, factory=True, workers=1, reload=True)
    except KeyboardInterrupt:
        print("Server stopped")
