"""
Configuration for cassiny-spawner.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
import os

log = logging.getLogger(__name__)


class Config():
    """General config class."""

    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # PUBLIC KEY
    try:
        with open("/keys/public_key.pub", mode="r", encoding="utf-8") as f:
            PUBLIC_KEY = f.read()
    except FileNotFoundError:
        PUBLIC_KEY = ""
        log.error("PRIVATE KEY not found.")

    # MCC
    # to locally run the server
    MCC_PUBLIC_URL = os.getenv("MCC_PUBLIC_URL", "https://mcc.cassiny.io")

    # internal url
    MCC_INTERNAL_URL = os.getenv(
        "MCC_INTERNAL_URL", "http://cassiny-auth")

    # STREAM
    STREAM_URI = os.getenv("STREAM_URI", "nats://127.0.0.1:4222")

    # DATABASE_URI
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
    DB_NAME = os.getenv("DB_NAME", "cassiny")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")

    # APPS #
    # public url to access apps
    APPS_PUBLIC_URL = "https://{subdomain}.cssny.space"

    # ip and port used by the jupyter notebook to run
    PROBE_DEFAULT_URL = "http://0.0.0.0:8888"
    PROBE_SESSION = "PROBE_USER_SESSION"

    # ip and port used to run api
    API_DEFAULT_URL = "http://0.0.0.0:8080"

    # ip and port used to run cargo
    CARGO_DEFAULT_URL = "http://0.0.0.0:9000"

    # QUOTA SERVICE
    QUOTA_IS_ACTIVE = True
    QUOTA_URI = 'http://cassiny-billing:8080/billing/quota'

    # LOGGING CONFIGURATION
    DEFAULT_LOGGING = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(levelname)s][%(filename)s:%(lineno)d]: %(asctime)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["console"],
                'propagate': False
            },
            "aiohttp.access": {
                "level": "DEBUG",
                "handlers": ["console"],
                'propagate': False
            }
        },
        "disable_existing_loggers": False
    }


class TestingConfig(Config):
    """Subclass of Config used for testing"""
    DEBUG = True
    TESTING = True

    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
    DB_NAME = os.getenv("DB_NAME", "cassiny_test")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
