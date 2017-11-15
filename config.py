"""
    config.py
    ~~~~~~~~~
    Configuration for mcc.cassiny.io

    :copyright: (c) 2017, Cassiny.io OÜ.
    All rights reserved.
"""

import os


class Config():
    """General config class.

    Other configs are subclass of Config.
    """
    # pylint: disable=too-few-public-methods

    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # PUBLIC KEY
    with open(os.path.join(BASE_DIR, "keys/jwtRS256.key.pub"), mode="r") as f:
        PUBLIC_KEY = f.read()

    # MCC
    # to locally run the server
    SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
    SERVER_PORT = os.getenv("SERVER_PORT", 8000)
    MCC_PUBLIC_URL = os.getenv("MCC_PUBLIC_URL", "https://mcc.cassiny.io")
    MCC_INTERNAL_URL = os.getenv(
        "MCC_INTERNAL_URL", "https://cassiny_nginx:8443")

    # KAFKA
    KAFKA_URI = os.getenv("KAFKA_URI", "localhost:9092")

    # REDIS
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)

    # DATABASE_URI
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
    DB_NAME = os.getenv("DB_NAME", "cassiny")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")

    # SECRET
    SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
    SECURITY_PASSWORD_SALT = os.getenv(
        "SECURITY_PASSWORD_SALT", "my_precious_two")

    # COOKIE
    MCC_COOKIE_NAME = "CASSINY_USER_SESSION"
    MCC_COOKIE_DOMAIN = os.getenv("MCC_COOKIE_DOMAIN", None)

    # APPS #
    # public url to access apps
    APPS_PUBLIC_URL = "http://{subdomain}.cssny.space"

    # ip and port used by the jupyter notebook to run
    PROBE_DEFAULT_URL = "http://0.0.0.0:8888"
    PROBE_SESSION = "PROBE_USER_SESSION"

    # ip and port used to run api
    API_DEFAULT_URL = "http://0.0.0.0:8080"

    # ip and port used to run cargo
    CARGO_DEFAULT_URL = "http://0.0.0.0:9000"

    # EMAIL
    EMAIL_API_KEY = "70be2afc6ad2c829bdad0eeeab64ea36dd7be168"
    EMAIL_API_URL = "https://api.sparkpost.com/api/v1/transmissions"

    # PAYMENT PROCESSORS

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
    # pylint: disable=too-few-public-methods
    DEBUG = True
    TESTING = True

    # COOKIE
    MCC_COOKIE_DOMAIN = None

    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
    DB_NAME = os.getenv("DB_NAME", "cassiny_test")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
