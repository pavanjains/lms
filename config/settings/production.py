import os
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email

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

# Instructor invitations. Off unless explicitly enabled; when enabled, the public origin must
# be a valid HTTPS origin and the sender a valid address, or the server refuses to start.
LMS_INSTRUCTOR_ONBOARDING_ENABLED = (
    os.environ.get("LMS_INSTRUCTOR_ONBOARDING_ENABLED", "false").strip().lower() == "true"
)
LMS_PUBLIC_ORIGIN = ""
LMS_INVITATION_FROM_EMAIL = ""
if LMS_INSTRUCTOR_ONBOARDING_ENABLED:
    _origin = os.environ.get("LMS_PUBLIC_ORIGIN", "").strip()
    _parts = urlsplit(_origin)
    if (_parts.scheme != "https" or not _parts.hostname or _parts.username or _parts.password
            or _parts.path not in {"", "/"} or _parts.query or _parts.fragment):
        raise ImproperlyConfigured(
            "Instructor onboarding requires LMS_PUBLIC_ORIGIN to be an HTTPS origin without a path."
        )
    _sender = os.environ.get("LMS_INVITATION_FROM_EMAIL", "").strip()
    try:
        validate_email(_sender)
    except ValidationError:
        raise ImproperlyConfigured(
            "Instructor onboarding requires a valid LMS_INVITATION_FROM_EMAIL."
        ) from None
    LMS_PUBLIC_ORIGIN = _origin.rstrip("/")
    LMS_INVITATION_FROM_EMAIL = _sender
