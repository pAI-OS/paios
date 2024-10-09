import asyncio
import os
import sys
import signal
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))
from common.paths import backend_dir, venv_dir, cert_dir
from common.config import logging_config
from backend.utils import get_env_key

# check environment
from backend.env import check_env
check_env()

# set up logging
from common.log import get_logger
logger = get_logger(__name__)

def handle_keyboard_interrupt(signum, frame):
    cleanup()
    asyncio.get_event_loop().stop()

def cleanup():
    # Perform any necessary cleanup here
    logger.info("Performing cleanup tasks.")

if __name__ == "__main__":
    # Set up signal handlers
    #signal.signal(signal.SIGINT, handle_keyboard_interrupt)
    #signal.signal(signal.SIGTERM, handle_keyboard_interrupt)

    # Ensure certificates are generated
    from common.cert import check_cert
    check_cert()

    # Create the app
    logger.info("Creating the app.")
    from app import create_app
    app = create_app()

    # Define host and port
    host = get_env_key("PAIOS_HOST", "localhost")
    port = int(get_env_key("PAIOS_PORT", 8443))

    # Log connection details
    logger.info(f"You can access pAI-OS at https://{host}:{port}.")
    logger.info("Bypass certificate warnings if using self-signed certificates.")

    # Run the app
    import uvicorn
    
    cert_path = cert_dir / "cert.pem"
    key_path = cert_dir / "key.pem"
    
    logger.info("Running the app with uvicorn.")
    try:
        uvicorn.run(
            "app:create_app", 
            host=host, 
            port=port, 
            factory=True, 
            workers=1, 
            reload=True, 
            reload_dirs=[backend_dir], 
            reload_excludes=[venv_dir], 
            log_config=logging_config,
            ssl_certfile=str(cert_path),
            ssl_keyfile=str(key_path),
            #ssl_keyfile_password=key_passphrase  # Pass the passphrase if the key is encrypted
        )
    except PermissionError as e:
        logger.error(f"Permission error: {e}. Ensure the application has access to the certificate and key files.")
    except KeyboardInterrupt:
        #handle_keyboard_interrupt(None, None)
        pass
    finally:
        cleanup()
