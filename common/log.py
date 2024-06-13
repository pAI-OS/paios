import json
import logging.config
import os
import yaml
import uvicorn.config
from common.paths import logging_config_path, log_dir

def setup_logging():
    os.makedirs(log_dir, exist_ok=True)
    setup_logging_basic_config()

def setup_logging_basic_config():
    # uvicorn embeds a default logging config in config.py that is marginally better than nothing (though it may not configure the root logger)
    def fallback_to_uvicorn_config():
        """Fallback to Uvicorn's default logging configuration"""
        logging.config.dictConfig(uvicorn.config.LOGGING_CONFIG)

    # allow override of logging config via environment variable so users don't have to overwrite repo file
    logging_config = os.getenv('PAIOS_LOG_CFG', None) if os.getenv('PAIOS_LOG_CFG', None) else logging_config_path
    if os.path.exists(logging_config):
        try:
            with open(logging_config, 'r') as f:
                if str(logging_config).endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            logging.config.dictConfig(config)
        except Exception as e:
            print(f"Failed to load custom logging config '{logging_config}': {e}")
            fallback_to_uvicorn_config()
    else:
        fallback_to_uvicorn_config()

# Set up logging configuration once on first import only
setup_logging()

# Define a function to get a logger
def get_logger(name):
    return logging.getLogger(name)
