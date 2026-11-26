import hashlib
import unicodedata
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.throttle_models import LoginThrottle

STUDENT = "student"
STAFF = "staff"
MAX_FAILURES = 15
WINDOW = timedelta(minutes=15)
LOCKOUT = timedelta(minutes=15)
PRUNE_AFTER = timedelta(days=1)
LOCKED_MESSAGE = "Too many failed sign-in attempts. Wait 15 minutes and try again."
FIRST_FAILURE = "first_failure"
LOCKED_OUT = "locked_out"


def _digest(identifier):
    normalized = unicodedata.normalize("NFKC", str(identifier)).strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def is_locked(scope, identifier, *, now=None):
    now = now or timezone.now()
    return LoginThrottle.objects.filter(
        scope=scope, key_digest=_digest(identifier), locked_until__gt=now,
    ).exists()


def record_failure(scope, identifier, *, now=None):
    """Count one failure. Returns FIRST_FAILURE, LOCKED_OUT, or None for any other attempt."""
    now = now or timezone.now()
    digest = _digest(identifier)
    outcome = None
    with transaction.atomic():
        LoginThrottle.objects.get_or_create(
            scope=scope, key_digest=digest, defaults={"window_started_at": now},
        )
        row = LoginThrottle.objects.select_for_update().get(scope=scope, key_digest=digest)
        if row.locked_until is not None and row.locked_until > now:
            return None
        if row.locked_until is not None or now - row.window_started_at >= WINDOW:
            row.failures, row.window_started_at, row.locked_until = 0, now, None
        row.failures += 1
        if row.failures >= MAX_FAILURES:
            row.locked_until = now + LOCKOUT
            outcome = LOCKED_OUT
        elif row.failures == 1:
            outcome = FIRST_FAILURE
        row.save(update_fields=["failures", "window_started_at", "locked_until"])
        LoginThrottle.objects.filter(
            window_started_at__lt=now - PRUNE_AFTER,
        ).exclude(locked_until__gt=now).delete()
    return outcome


def reset(scope, identifier):
    LoginThrottle.objects.filter(scope=scope, key_digest=_digest(identifier)).delete()
