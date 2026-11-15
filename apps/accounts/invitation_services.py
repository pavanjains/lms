import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.backends import is_active_staff
from apps.accounts.models import InstructorInvitation
from apps.organizations.models import Organization


def _digest(token):
    if not isinstance(token, str) or not 20 <= len(token) <= 256:
        raise ValidationError("Invitation is invalid or unavailable.")
    return hashlib.sha256(token.encode()).hexdigest()


def _lock_owner_organization(actor):
    verifier = getattr(actor, "is_verified", None)
    if (not is_active_staff(actor) or actor.role != "OWNER"
            or not callable(verifier) or not verifier()):
        raise PermissionDenied
    organization = Organization.objects.select_for_update().get(pk=actor.organization_id)
    User = get_user_model()
    if not organization.is_active or not User.objects.filter(
        pk=actor.pk, organization=organization, role="OWNER", is_active=True,
    ).exists():
        raise PermissionDenied
    return organization


@transaction.atomic
def issue_instructor_invitation(*, actor, email):
    organization = _lock_owner_organization(actor)
    email = email.strip().lower()
    validate_email(email)
    User = get_user_model()
    if User.objects.filter(email__iexact=email, role__in=["OWNER", "INSTRUCTOR"]).exists():
        raise ValidationError("A staff account already uses this email.")
    hours = int(getattr(settings, "LMS_INVITATION_HOURS", 48))
    if not 1 <= hours <= 168:
        raise ValidationError("Invitation lifetime must be between 1 and 168 hours.")
    now = timezone.now()
    InstructorInvitation.objects.filter(
        organization=organization, email__iexact=email,
        accepted_at__isnull=True, revoked_at__isnull=True,
    ).update(revoked_at=now)
    token = secrets.token_urlsafe(32)
    invitation = InstructorInvitation(
        organization=organization, created_by_id=actor.pk, email=email,
        token_digest=_digest(token), expires_at=now + timedelta(hours=hours),
    )
    invitation.full_clean()
    invitation.save()
    return invitation, token


@transaction.atomic
def revoke_instructor_invitation(*, actor, invitation_id):
    organization = _lock_owner_organization(actor)
    invitation = InstructorInvitation.objects.select_for_update().filter(
        pk=invitation_id, organization=organization,
    ).first()
    if invitation is None:
        raise PermissionDenied
    if invitation.accepted_at:
        raise ValidationError("An accepted invitation cannot be revoked.")
    if invitation.revoked_at is None:
        invitation.revoked_at = timezone.now()
        invitation.save(update_fields=["revoked_at"])
    return invitation


def accept_instructor_invitation(*, token, username, password):
    digest = _digest(token)
    try:
        with transaction.atomic():
            return _accept_locked(digest, username, password)
    except IntegrityError:
        raise ValidationError("Account details conflict with an existing account.") from None


def _accept_locked(digest, username, password):
    candidate = InstructorInvitation.objects.filter(token_digest=digest).values(
        "pk", "organization_id",
    ).first()
    if candidate is None:
        raise ValidationError("Invitation is invalid or unavailable.")
    # Consistent lock order: organization, then invitation.
    organization = Organization.objects.select_for_update().get(pk=candidate["organization_id"])
    invitation = InstructorInvitation.objects.select_for_update().get(pk=candidate["pk"])
    now = timezone.now()
    if (not organization.is_active or invitation.revoked_at or invitation.accepted_at
            or invitation.expires_at <= now):
        raise ValidationError("Invitation is invalid or unavailable.")
    if not get_user_model().objects.filter(
        pk=invitation.created_by_id, organization=organization, role="OWNER", is_active=True,
    ).exists():
        raise ValidationError("Invitation is invalid or unavailable.")
    User = get_user_model()
    user = User(
        organization=organization, username=User.normalize_username(username.strip()),
        email=invitation.email, role=User.Role.INSTRUCTOR, is_active=True,
        is_staff=False, is_superuser=False,
    )
    validate_password(password, user=user)
    user.set_password(password)
    user.full_clean()
    user.save()
    invitation.accepted_user = user
    invitation.accepted_at = now
    invitation.save(update_fields=["accepted_user", "accepted_at"])
    return user
