from .base import *

SECRET_KEY = "django-insecure-*$j$%n!l088o3#=crm2b)_axpg8r24sv8y9fh&co(sm^jgd#f$"

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
