"""
Django settings for accurate_replica project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
from hashlib import sha512
import logging
import os
import sys

from django.utils import timezone
import environ


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load env vars and set defaults
env = environ.Env(DEBUG=(bool, False), ENV=(str, "prod"), HTTPS=(bool, True))
environ.Env.read_env()  # read env file
ENV = env("ENV")

# We store apps in apps directory so we need to add to the sys.path
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
HOSTNAME = env("HOSTNAME")
HTTPS = env("HTTPS")
URL = FQDN = f'http{"s" if HTTPS else ""}://{HOSTNAME}'

# HTTPS & SSL Redirects
SECURE_SSL_REDIRECT = SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_AGE = 28800  # 8 hours in seconds

LOGIN_URL = "/login/auth0"
LOGIN_REDIRECT_URL = "/dashboard"
LOGOUT_REDIRECT_URL = "/"
LOGIN_ERROR_URL = "/authentication/auth-error"
APPEND_SLASH = True

ADMIN_SITE_URL = sha512(f"accurate-replica-{ENV}".encode("utf-8")).hexdigest()[:16]

ALLOWED_HOSTS = ["localhost", HOSTNAME]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party noise
    "django_s3_storage",
    "raven.contrib.django.raven_compat",
    "social_django",
    # our applications
    "core",
    "authentication",
    "fax",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "accurate_replica.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "accurate_replica.wsgi.application"

# User Model
AUTH_USER_MODEL = "authentication.User"

# Email configuration
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = env("SENDGRID_SANDBOX_MODE_IN_DEBUG") or not DEBUG

# Auth0
AUTH0_DOMAIN = env("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = env("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env("AUTH0_CLIENT_SECRET")

SOCIAL_AUTH_AUTH0_DOMAIN = AUTH0_DOMAIN
SOCIAL_AUTH_AUTH0_KEY = AUTH0_CLIENT_ID
SOCIAL_AUTH_AUTH0_SCOPE = ["openid", "email", "profile"]
SOCIAL_AUTH_AUTH0_SECRET = AUTH0_CLIENT_SECRET
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
SOCIAL_AUTH_LOGIN_ERROR_URL = "/authentication/auth-error"
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_TRAILING_SLASH = False
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "authentication.pipeline.get_or_create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.social_auth.associate_by_email",
    "authentication.pipeline.cycle_user_auth_token",
)

# https://github.com/omab/python-social-auth/issues/534
SESSION_COOKIE_SAMESITE = None
SOCIAL_AUTH_REDIRECT_IS_HTTPS = HTTPS


# Sentry
RAVEN_DSN = env("RAVEN_DSN")
RELEASE = timezone.now().isoformat()  # raven.fetch_git_sha(os.path.abspath(os.pardir))

RAVEN_CONFIG = {
    "dsn": RAVEN_DSN,
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    "release": RELEASE,
}


# Twilio
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = DEFAULT_FROM_NUMBER = env("DEFAULT_FROM_NUMBER")
TWILIO_NUMBER_SID = env("TWILIO_NUMBER_SID")


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {"default": env.db()}
REDIS_URL = env("REDIS_URL")
CELERY_BROKER_URL = REDIS_URL

# Media
MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = S3_BUCKET_NAME = env("S3_BUCKET_NAME")
AWS_S3_ADDRESSING_STYLE = "auto"
AWS_S3_KEY_PREFIX = "app-content"
AWS_S3_ENCRYPT_KEY = True


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
