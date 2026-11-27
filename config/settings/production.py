import os
import re
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

# HTTPS behind a proxy. Every value below comes from the environment, is validated, and defaults
# to the safe choice, so the same code runs on any host. See docs/DEPLOYMENT_SETTINGS.md.
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False  # never enabled here: preload is hard to undo
SECURE_PROXY_SSL_HEADER = None
CSRF_TRUSTED_ORIGINS = []

_hsts = os.environ.get("LMS_HSTS_SECONDS", "").strip() or "0"
if not (_hsts.isascii() and _hsts.isdigit()) or int(_hsts) > 31536000:
    raise ImproperlyConfigured("LMS_HSTS_SECONDS must be a whole number from 0 to 31536000.")
SECURE_HSTS_SECONDS = int(_hsts)

_subdomains = os.environ.get("LMS_HSTS_INCLUDE_SUBDOMAINS", "").strip().lower()
if _subdomains not in {"", "true", "false"}:
    raise ImproperlyConfigured("LMS_HSTS_INCLUDE_SUBDOMAINS must be true or false.")
SECURE_HSTS_INCLUDE_SUBDOMAINS = _subdomains == "true" and SECURE_HSTS_SECONDS > 0

# Name of the request header (in Django's META form, for example HTTP_X_FORWARDED_PROTO) that the
# hosting proxy always sets itself, overwriting any value sent by the client. Leave unset unless
# the host's documentation confirms that behavior.
_proxy_header = os.environ.get("LMS_PROXY_SSL_HEADER", "").strip()
if _proxy_header:
    if not re.fullmatch(r"HTTP_[A-Z0-9_]+", _proxy_header):
        raise ImproperlyConfigured(
            "LMS_PROXY_SSL_HEADER must be a request header name such as HTTP_X_FORWARDED_PROTO."
        )
    SECURE_PROXY_SSL_HEADER = (_proxy_header, "https")

for _item in os.environ.get("LMS_CSRF_TRUSTED_ORIGINS", "").split(","):
    _item = _item.strip()
    if not _item:
        continue
    _parts = urlsplit(_item)
    if (_parts.scheme != "https" or not _parts.hostname or "*" in _parts.netloc
            or _parts.username or _parts.password or _parts.path not in {"", "/"}
            or _parts.query or _parts.fragment):
        raise ImproperlyConfigured(
            "LMS_CSRF_TRUSTED_ORIGINS must list HTTPS origins without a path or wildcard."
        )
    CSRF_TRUSTED_ORIGINS.append("https://" + _parts.netloc)

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
