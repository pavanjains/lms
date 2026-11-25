import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("local-"):  # noqa: F405
    raise ImproperlyConfigured("Set a strong production DJANGO_SECRET_KEY of at least 50 characters.")
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("Production requires explicit DJANGO_ALLOWED_HOSTS.")
if (os.environ.get("LMS_DEPLOYMENT_MODE", "production") == "local"
        or os.environ.get("LMS_LOCAL_MFA_POLICY_ENABLED", "false").strip().lower() not in {"", "false"}
        or os.environ.get("LMS_INSTALLATION_ADMIN_USERNAME", "").strip()):
    raise ImproperlyConfigured("Local MFA policy controls must not be configured in production.")
LMS_DEPLOYMENT_MODE = "production"
LMS_LOCAL_MFA_POLICY_ENABLED = False
LMS_INSTALLATION_ADMIN_USERNAME = ""
DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Configure trusted proxy headers only after reviewing the actual hosting topology.
