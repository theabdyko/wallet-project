"""
Development settings for wallet project.
"""

from .base import *  # noqa
from .base import LOGGING
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Ensure PostgreSQL is used in development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="wallet_db"),
        "USER": config("DB_USER", default="wallet_user"),
        "PASSWORD": config("DB_PASSWORD", default="wallet_password"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "client_encoding": "UTF8",
        },
        "CONN_MAX_AGE": 60,  # Connection pooling
        "ATOMIC_REQUESTS": True,  # Enable transaction management
    }
}

# Logging
DEV_LOG_LEVEL = config("DEV_LOG_LEVEL", default="DEBUG")
DEV_LOG_DB_LEVEL = config("DEV_LOG_DB_LEVEL", default="DEBUG")

LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": DEV_LOG_DB_LEVEL,
    "propagate": False,
}

# Set root logger to DEBUG for development
LOGGING["root"]["level"] = DEV_LOG_LEVEL

