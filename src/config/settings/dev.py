from .base import *

SECRET_KEY = ENV.str("SECRET_KEY", "")

DEBUG = True

ALLOWED_HOSTS = ENV.list("ALLOWED_HOSTS", default=[])
CORS_ALLOWED_ORIGINS = ENV.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
