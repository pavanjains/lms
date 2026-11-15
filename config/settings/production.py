from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("local-"):  # noqa: F405
    raise ImproperlyConfigured("Set a strong production DJANGO_SECRET_KEY of at least 50 characters.")
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("Production requires explicit DJANGO_ALLOWED_HOSTS.")
DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Configure trusted proxy headers only after reviewing the actual hosting topology.
