from django.urls import path

from apps.accounts.onboarding import invite
from apps.accounts.owner_views import instructor_management, revoke_invitation

app_name = "owner-accounts"
urlpatterns = [
    path("instructors/", instructor_management, name="instructors"),
    path("invitations/new/", invite, name="invite"),
    path("invitations/<int:invitation_id>/resend/", invite, name="resend-invitation"),
    path("invitations/<int:invitation_id>/revoke/", revoke_invitation, name="revoke-invitation"),
]
