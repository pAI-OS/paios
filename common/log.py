import json
import logging.config
import os
import yaml
import uvicorn.config
from common.paths import log_dir
from common.config import logging_config

def setup_logging():
    os.makedirs(log_dir, exist_ok=True)
    setup_logging_basic_config()

def setup_logging_basic_config():
    # uvicorn embeds a default logging config in config.py that is marginally better than nothing (though it may not configure the root logger)
    try:
        logging.config.dictConfig(logging_config)
    except Exception as e:
        print(f"Failed to load custom logging config '{logging_config}': {e}")
        logging.config.dictConfig(uvicorn.config.LOGGING_CONFIG)
    else:
        logging.config.dictConfig(uvicorn.config.LOGGING_CONFIG)

# Set up logging configuration once on first import only
setup_logging()

# Define a function to get a logger
def get_logger(name):
    return logging.getLogger(name)
