import os

os.environ.setdefault("DJANGO_SECRET_KEY", "local-development-only-not-for-deployment")
os.environ.setdefault("POSTGRES_PASSWORD", "local-development-only-change-me")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
from .base import *  # noqa: F403, E402

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
LMS_INSTRUCTOR_ONBOARDING_ENABLED = os.environ.get("LMS_INSTRUCTOR_ONBOARDING_ENABLED", "false").lower() == "true"
LMS_PUBLIC_ORIGIN = os.environ.get("LMS_PUBLIC_ORIGIN", "http://localhost:8000")
LMS_INVITATION_FROM_EMAIL = os.environ.get("LMS_INVITATION_FROM_EMAIL", "noreply@example.test")
