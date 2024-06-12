import json
import logging.config
import os
import yaml
import uvicorn.config
from common.paths import logging_config_path

def setup_logging(
    default_path=logging_config_path,
    default_level=logging.INFO,
    env_key='PAIOS_LOG_CFG' # to override the default configuration without editing files in repo
):
    
    setup_logging_basic_config()

def setup_logging_basic_config(
    default_path=logging_config_path,
    default_level=logging.INFO,
    env_key='PAIOS_LOG_CFG' # to override the default configuration without editing files in repo
):
    def fallback_to_uvicorn_config():
        """Fallback to Uvicorn's default logging configuration"""
        logging.config.dictConfig(uvicorn.config.LOGGING_CONFIG)

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value

    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                if str(path).endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            logging.config.dictConfig(config)
        except Exception as e:
            print(f"Failed to load custom logging config '{path}': {e}")
            fallback_to_uvicorn_config()
    else:
        fallback_to_uvicorn_config()

# Set up logging configuration once on first import only
setup_logging()

# Define a function to get a logger
def get_logger(name):
    return logging.getLogger(name)
