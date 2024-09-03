from typing import Any
from common.paths import log_dir

logging_config: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
        "uvicorn_default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(client_addr)s - - [%(asctime)s] "%(request_line)s" %(status_code).3s -',
            "datefmt": "%d/%b/%Y:%H:%M:%S %z",
            "use_colors": False
        },

    },
    "handlers": {
        # TODO: standardise formatting; for now use uvicorn_default
        "default": {
            #"formatter": "standard",
            "formatter": "uvicorn_default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "standard": {
            #"formatter": "standard",
            "formatter": "uvicorn_default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "uvicorn_default": {
            "formatter": "uvicorn_default",
            #"formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / "access.log",
            "maxBytes": 52428800,
            "backupCount": 9,
            "encoding": "utf8"
        },
        "connexion": {
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / "connexion.log",
            "maxBytes": 52428800,
            "backupCount": 9,
            "encoding": "utf8"
        },
        "backend.redirector": {
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / "redirector.log",
            "maxBytes": 52428800,
            "backupCount": 9,
            "encoding": "utf8"
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"}, # root logger
        "connexion": {"handlers": ["connexion"], "level": "DEBUG", "propagate": False},
        "backend.redirector": {"handlers": ["backend.redirector"], "level": "INFO", "propagate": False},
        "uvicorn": {"handlers": ["uvicorn_default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "watchfiles.main": {"level": "ERROR"}, # filter watchfiles noise
        "sqlalchemy.engine": {"level": "WARNING", "propagate": False}, # filter sqlalchemy noise
    },
}
