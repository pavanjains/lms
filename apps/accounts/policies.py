from functools import wraps

from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache

from apps.accounts.backends import is_active_staff


def staff_mfa_required(view):
    """Require active staff and verified MFA on every protected request."""

    @wraps(view)
    def guarded(request, *args, **kwargs):
        user = request.user
        if not is_active_staff(user):
            raise PermissionDenied
        verifier = getattr(user, "is_verified", None)
        if not callable(verifier) or not verifier():
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return never_cache(guarded)
