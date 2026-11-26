import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.accounts import throttle
from apps.accounts.audit_models import AuditEvent, AuditEventType

logger = logging.getLogger(__name__)

ALLOWED_DETAIL = frozenset({"role", "name_digest", "classroom_name"})
STAFF_ROLES = ("OWNER", "INSTRUCTOR")
DEFAULT_RETENTION_DAYS = 90


def retention_days():
    value = getattr(settings, "LMS_AUDIT_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)
    if type(value) is not int or not 1 <= value <= 3650:
        raise ImproperlyConfigured("LMS_AUDIT_RETENTION_DAYS must be a whole number from 1 to 3650.")
    return value


def record(event_type, *, actor=None, subject=None, organization_id=None,
           classroom_id=None, detail=None):
    """Write one append-only event. Call inside the transaction of the action it records."""
    if event_type not in AuditEventType.values:
        raise ValueError("Unknown audit event type.")
    detail = dict(detail or {})
    if set(detail) - ALLOWED_DETAIL:
        raise ValueError("Audit detail key is not allowed.")
    if any(not isinstance(value, str) or len(value) > 150 for value in detail.values()):
        raise ValueError("Audit detail values must be short strings.")
    if organization_id is None:
        for person in (actor, subject):
            if person is not None:
                organization_id = person.organization_id
                break
    event = AuditEvent(
        event_type=event_type, organization_id=organization_id,
        actor=actor, actor_username=actor.username if actor is not None else "",
        subject=subject, subject_username=subject.username if subject is not None else "",
        classroom_id=classroom_id, detail=detail,
    )
    event.full_clean(exclude=["organization", "actor", "subject"])
    event.save()
    return event


def _best_effort(write):
    """Sign-in events must never block signing in; a failed write is logged without details."""
    try:
        with transaction.atomic():
            write()
    except DatabaseError:
        logger.exception("Audit event could not be written.")


def record_sign_in(user):
    if getattr(user, "role", None) not in (*STAFF_ROLES, "STUDENT"):
        return
    _best_effort(lambda: record(
        AuditEventType.SIGN_IN_SUCCESS, actor=user, detail={"role": user.role},
    ))


def _known_account(scope, identifier):
    text = str(identifier).strip()
    if not text:
        return None
    User = get_user_model()
    if scope == throttle.STUDENT:
        return User.objects.filter(role="STUDENT", username=User.normalize_username(text)).first()
    return User.objects.filter(role__in=STAFF_ROLES, email__iexact=text).first()


def record_failed_sign_in(scope, identifier, outcome):
    """Record only the first failure in a window and the lockout, never every attempt.

    The typed name is never stored: only a short digest, plus the matching account
    when one exists. Unknown names produce an event with no organization.
    """
    if outcome == throttle.FIRST_FAILURE:
        event_type = AuditEventType.SIGN_IN_FAILED
    elif outcome == throttle.LOCKED_OUT:
        event_type = AuditEventType.SIGN_IN_LOCKED
    else:
        return

    def write():
        record(event_type, subject=_known_account(scope, identifier),
               detail={"name_digest": throttle._digest(identifier)[:16]})

    _best_effort(write)


def purge_expired(*, now=None):
    now = now or timezone.now()
    deleted, _ = AuditEvent.objects.filter(
        created_at__lt=now - timedelta(days=retention_days()),
    ).delete()
    return deleted
