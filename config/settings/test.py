import os

os.environ.setdefault("DJANGO_SECRET_KEY", "unit-tests-only-not-for-deployment")
os.environ.setdefault("POSTGRES_PASSWORD", "test-only")
from .base import *  # noqa: F403, E402

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
ALLOWED_HOSTS = ["testserver", "localhost"]
