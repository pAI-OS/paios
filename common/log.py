import logging.config
import os
from common.paths import log_dir
from common.config import logging_config

def setup_logging():
    os.makedirs(log_dir, exist_ok=True)
    logging.config.dictConfig(logging_config) # could fallback to uvicorn.config.LOGGING_CONFIG but requires import that may not be available pre-setup/check_env

# Set up logging configuration once on first import only
setup_logging()

# Define a function to get a logger
def get_logger(name):
    return logging.getLogger(name)
