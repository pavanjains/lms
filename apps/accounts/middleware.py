import math
import time

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, logout
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control
from django.utils.deprecation import MiddlewareMixin
from two_factor.utils import default_device

from apps.accounts.backends import is_active_staff
from apps.accounts.mfa_policy import relax_verification

STAFF_BACKEND = "apps.accounts.backends.StaffEmailBackend"
STAFF_STARTED = "staff_started_at"
STAFF_SEEN = "staff_last_seen"
CLOCK_SKEW_SECONDS = 5
START, VALID, EXPIRED = "start", "valid", "expired"


def staff_path(path):
    return path.startswith(("/account/", "/staff/"))


def staff_limits():
    idle = int(settings.LMS_STAFF_IDLE_SECONDS)
    absolute = int(settings.LMS_STAFF_ABSOLUTE_SECONDS)
    if not 1 <= idle <= absolute <= 86400:
        raise ImproperlyConfigured("Invalid staff session limits.")
    return idle, absolute


def clock_state(started, seen, now, idle, absolute):
    """START when the session has no clock yet, EXPIRED when it is over a limit or its
    timestamps are missing, malformed or out of order, otherwise VALID."""
    if started is None and seen is None:
        return START
    for value in (started, seen):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return EXPIRED
    if started > seen or seen > now + CLOCK_SKEW_SECONDS:
        return EXPIRED
    if now - seen >= idle or now - started >= absolute:
        return EXPIRED
    return VALID


class StaffSessionMiddleware(MiddlewareMixin):
    """Idle and absolute limits for staff sessions. Only staff pages renew the idle clock; the
    absolute clock is never renewed. Expiry is enforced on the next request."""

    def process_request(self, request):
        if (request.session.get(BACKEND_SESSION_KEY) != STAFF_BACKEND
                or not request.user.is_authenticated):
            return
        now = time.time()
        idle, absolute = staff_limits()
        started = request.session.get(STAFF_STARTED)
        seen = request.session.get(STAFF_SEEN)
        state = clock_state(started, seen, now, idle, absolute)
        if state == EXPIRED:
            logout(request)
            return
        if state == START:
            started = seen = now
            request.session[STAFF_STARTED] = started
            request.session[STAFF_SEEN] = seen
        if staff_path(request.path_info):
            request.session[STAFF_SEEN] = now
            request.session.set_expiry(max(1, int(min(idle, absolute - (now - started)))))


class StaffAuthMiddleware(MiddlewareMixin):
    """Keep first-factor enrollment sessions out of all staff business pages."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Local-only: with the installation policy off, password-only staff count as verified.
        relax_verification(request)
        if not staff_path(request.path_info):
            return None
        if not settings.LMS_STAFF_AUTH_ENABLED:
            raise Http404
        match = request.resolver_match
        name = match.url_name
        factor_route = match.namespace == "two_factor"
        if not request.user.is_authenticated:
            if factor_route and name == "login":
                return None
            return redirect("two_factor:login")
        if not is_active_staff(request.user):
            if getattr(request.user, "role", None) != "STUDENT":
                logout(request)
            raise PermissionDenied
        if name in {"staff-entry", "staff-logout"} and not factor_route:
            return None
        if factor_route and name == "login":
            return None
        if factor_route and name in {"setup", "qr"} and not default_device(request.user):
            return None
        if not request.user.is_verified():
            return redirect("two_factor:login")
        return None

    def process_response(self, request, response):
        if staff_path(request.path_info):
            patch_cache_control(response, private=True, no_store=True, no_cache=True,
                                max_age=0, must_revalidate=True)
        return response
