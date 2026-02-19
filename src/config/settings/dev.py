from .base import *

SECRET_KEY = "django-insecure-*$j$%n!l088o3#=crm2b)_axpg8r24sv8y9fh&co(sm^jgd#f$"

DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
