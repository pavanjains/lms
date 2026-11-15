from django.contrib.auth.views import LogoutView
from django.urls import include, path
from two_factor.urls import urlpatterns as two_factor_urls

from apps.accounts.staff_views import StaffLoginView, deny_mfa_disable, staff_entry, staff_home
from apps.core.views import home, liveness

# Override only login and disable; retain upstream namespace and enrollment routes.
tf_patterns, tf_namespace = two_factor_urls
staff_factor_patterns = [
    path("account/login/", StaffLoginView.as_view(), name="login"),
    path("account/two_factor/disable/", deny_mfa_disable, name="disable"),
] + [pattern for pattern in tf_patterns if pattern.name not in {"login", "disable"}]

urlpatterns = [
    path("", home, name="home"),
    path("health/live/", liveness, name="liveness"),
    path("", include((staff_factor_patterns, tf_namespace))),
    path("staff/entry/", staff_entry, name="staff-entry"),
    path("staff/", staff_home, name="staff-home"),
    path("staff/logout/", LogoutView.as_view(), name="staff-logout"),
]
