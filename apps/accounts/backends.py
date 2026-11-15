from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


def is_active_staff(user):
    return (
        user is not None
        and user.is_authenticated
        and user.is_active
        and user.role in {"OWNER", "INSTRUCTOR"}
        and user.organization.is_active
    )


class StaffEmailBackend(ModelBackend):
    """Staff-only first-factor authentication, not proof of MFA verification."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        identifier = kwargs.get("email") or username
        if not isinstance(identifier, str) or not isinstance(password, str):
            return None
        identifier = identifier.strip()
        candidates = list(User.objects.select_related("organization").filter(
            email__iexact=identifier,
            role__in=[User.Role.OWNER, User.Role.INSTRUCTOR],
        )[:2])
        if len(candidates) != 1:
            User().set_password(password)
            return None
        user = candidates[0]
        if user.check_password(password) and is_active_staff(user):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            user = User.objects.select_related("organization").get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if is_active_staff(user) else None
