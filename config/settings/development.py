import os

os.environ.setdefault("DJANGO_SECRET_KEY", "local-development-only-not-for-deployment")
os.environ.setdefault("POSTGRES_PASSWORD", "local-development-only-change-me")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
from .base import *  # noqa: F403, E402

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
