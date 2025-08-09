"""
Production settings for wallet project.
"""
from .base import *  # noqa
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False



# Database - PostgreSQL with production-specific settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="wallet_db_prod"),
        "USER": config("DB_USER", default="wallet_user_prod"),
        "PASSWORD": config("DB_PASSWORD", default="wallet_password_prod"),
        "HOST": config("DB_HOST", default="prod-db.example.com"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "client_encoding": "UTF8",
            "sslmode": "require",  # Require SSL in production
            "connect_timeout": 10,  # Connection timeout
        },
        "CONN_MAX_AGE": 300,  # Longer connection pooling for production
        "ATOMIC_REQUESTS": True,
        "AUTOCOMMIT": False,
        "CONN_HEALTH_CHECKS": True,  # Enable connection health checks
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config(
    "SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
)
X_FRAME_OPTIONS = config("X_FRAME_OPTIONS", default="DENY")
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=bool
)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=True, cast=bool)

# HTTPS settings
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)

# Static files
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Database connection pooling and performance
DB_CONN_MAX_AGE = config("DB_CONN_MAX_AGE", default=300, cast=int)
DB_OPTIONS = {
    "client_encoding": "UTF8",
    "sslmode": "require",
    "connect_timeout": 10,
    "application_name": "wallet_project_prod",
}
