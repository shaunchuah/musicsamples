import os

# Sentry Monitoring
import sentry_sdk
from decouple import Csv, config
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from unipath import Path

# import dj_database_url


sentry_sdk.init(
    dsn="https://565f64fc7bea4af39487c5f0edcdab0b@o482942.ingest.sentry.io/5533900",
    integrations=[DjangoIntegration(), RedisIntegration()],
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = Path(__file__).parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)

# load production server from .env
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "simple_history",
    "django_select2",
    "rest_framework",
    "rest_framework.authtoken",
    "storages",
    "django_filters",
    "taggit",
    "app",  # Enable the inner app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "core.urls"
LOGIN_REDIRECT_URL = "home"  # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py
TEMPLATE_DIR = os.path.join(BASE_DIR, "core/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE"),
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", cast=int),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "GB"

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, "core/static"),)
#############################################################
#############################################################
EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")

DEFAULT_FROM_EMAIL = "SampleTrek <password_reset@musicstudy.uk>"

# POST SSL DEPLOYMENT SETTINGS
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", cast=int)
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config("SECURE_CONTENT_TYPE_NOSNIFF", cast=bool)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
}

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/uploads/"

# CACHING

CACHES = {
    "default": {
        "BACKEND": config("DEFAULT_CACHE_BACKEND"),
        "LOCATION": config("DEFAULT_CACHE_LOCATION"),
        "OPTIONS": {
            "CLIENT_CLASS": config("CLIENT_CLASS"),
        },
    },
}

# Set the cache backend to select2
SELECT2_CACHE_BACKEND = "default"

INTERNAL_IPS = ["127.0.0.1"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
