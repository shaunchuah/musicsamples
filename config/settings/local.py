# ruff: noqa: E501
from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "testserver", "host.docker.internal"]

# AZURE STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY")
AZURE_STORAGE_CONNECTION_STRING = env("AZURE_STORAGE_CONNECTION_STRING")
AZURE_ACCOUNT_NAME = "gutresearch"
AZURE_CONTAINER_NAME = "gtrac-store-dev"


# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "azure_container": AZURE_CONTAINER_NAME,
            "connection_string": AZURE_STORAGE_CONNECTION_STRING,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]

# Django Debug Toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    *MIDDLEWARE,
]


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025


SITE_URL = "http://127.0.0.1:8000"
