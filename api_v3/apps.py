# api_v3/apps.py
# Declares the Django application config for the v3 API package.
# Exists so Django can register the dedicated api_v3 app that serves frontend-facing endpoints.

from django.apps import AppConfig


class ApiV3Config(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "api_v3"
    verbose_name = "API v3"
