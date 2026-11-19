from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control
from django.utils.deprecation import MiddlewareMixin
from two_factor.utils import default_device

from apps.accounts.backends import is_active_staff


def staff_path(path):
    return path.startswith(("/account/", "/staff/"))


class StaffAuthMiddleware(MiddlewareMixin):
    """Keep first-factor enrollment sessions out of all staff business pages."""

    def process_view(self, request, view_func, view_args, view_kwargs):
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
