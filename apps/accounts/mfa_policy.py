from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError, transaction
from django.views.decorators.debug import sensitive_variables

from apps.accounts.backends import is_active_staff
from apps.accounts.mfa_policy_models import InstallationMfaPolicy, InstallationMfaPolicyAudit
from apps.organizations.models import Organization


def local_controls_enabled():
    return (getattr(settings, "LMS_DEPLOYMENT_MODE", "production") == "local"
            and getattr(settings, "LMS_LOCAL_MFA_POLICY_ENABLED", False) is True
            and getattr(settings, "LMS_STAFF_AUTH_ENABLED", False) is True)


def installation_owner(actor):
    username = getattr(settings, "LMS_INSTALLATION_ADMIN_USERNAME", "")
    if (not local_controls_enabled() or not isinstance(username, str) or not username
            or not getattr(actor, "is_authenticated", False) or not getattr(actor, "pk", None)):
        raise PermissionDenied
    user = get_user_model().objects.select_related("organization").filter(
        pk=actor.pk, username=username, organization_id=getattr(actor, "organization_id", None),
        role="OWNER", is_active=True, organization__is_active=True,
    ).first()
    if user is None:
        raise PermissionDenied
    return user


def may_manage_policy(actor):
    try:
        installation_owner(actor)
    except PermissionDenied:
        return False
    return True


def read_policy():
    try:
        return InstallationMfaPolicy.objects.get(pk=1)
    except InstallationMfaPolicy.DoesNotExist:
        raise ValidationError("Installation security policy is unavailable. Review migration status.") from None


def require_policy_mfa(actor, policy):
    verifier = getattr(actor, "is_verified", None)
    if policy.require_mfa and (not callable(verifier) or not verifier()):
        raise PermissionDenied


def effective_mfa_required():
    """MFA is required unless explicit local controls are on and the stored policy is off."""
    if not local_controls_enabled():
        return True
    try:
        return InstallationMfaPolicy.objects.values_list("require_mfa", flat=True).get(pk=1)
    except (InstallationMfaPolicy.DoesNotExist, DatabaseError):
        return True


def relax_verification(request):
    """With the local policy off, a password-only active staff session counts as verified.

    Real OTP verification is untouched, so turning the policy back on makes
    password-only sessions fail every is_verified() check again. Students never qualify.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or not local_controls_enabled():
        return
    if getattr(user, "role", None) not in {"OWNER", "INSTRUCTOR"}:
        return
    if is_active_staff(user) and not effective_mfa_required():
        user.is_verified = lambda: True


@sensitive_variables()
@transaction.atomic
def change_policy(*, actor, require_mfa, expected_version, password, confirmed):
    candidate = installation_owner(actor)
    policy = InstallationMfaPolicy.objects.select_for_update().filter(pk=1).first()
    if policy is None:
        raise ValidationError("Installation security policy is unavailable.")
    organization = Organization.objects.select_for_update().filter(
        pk=candidate.organization_id, is_active=True,
    ).first()
    owner = get_user_model().objects.select_for_update().filter(
        pk=candidate.pk, username=getattr(settings, "LMS_INSTALLATION_ADMIN_USERNAME", ""),
        organization=organization, is_active=True, role="OWNER",
    ).first() if organization else None
    if owner is None:
        raise PermissionDenied
    require_policy_mfa(actor, policy)
    if type(require_mfa) is not bool or confirmed is not True:
        raise ValidationError("Review and explicitly confirm a Boolean policy choice.")
    if type(expected_version) is not int or expected_version < 1 or policy.version != expected_version:
        raise ValidationError("Policy changed. Reload and review again.")
    if not isinstance(password, str) or not password or not owner.check_password(password):
        raise ValidationError("Current password confirmation failed.")
    if require_mfa == policy.require_mfa:
        raise ValidationError("No policy change to save.")
    previous = policy.require_mfa
    policy.require_mfa = require_mfa
    policy.version += 1
    policy.full_clean()
    policy.save(update_fields=["require_mfa", "version", "updated_at"])
    event = InstallationMfaPolicyAudit(
        policy_version=policy.version, previous_required=previous, new_required=require_mfa,
        changed_by=owner, actor_username=owner.username,
    )
    event.full_clean()
    event.save()
    return policy
