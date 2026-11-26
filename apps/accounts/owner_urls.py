from django.urls import path

from apps.accounts import mfa_policy_views
from apps.accounts.audit_views import audit_log
from apps.accounts.deactivation import deactivate
from apps.accounts.onboarding import invite
from apps.accounts.owner_views import instructor_management, revoke_invitation

app_name = "owner-accounts"
urlpatterns = [
    path("security/mfa/", mfa_policy_views.settings_view, name="mfa-policy"),
    path("audit/", audit_log, name="audit-log"),
    path("instructors/", instructor_management, name="instructors"),
    path("instructors/<int:instructor_id>/deactivate/", deactivate, name="deactivate-instructor"),
    path("invitations/new/", invite, name="invite"),
    path("invitations/<int:invitation_id>/resend/", invite, name="resend-invitation"),
    path("invitations/<int:invitation_id>/revoke/", revoke_invitation, name="revoke-invitation"),
]
