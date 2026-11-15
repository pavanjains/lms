from django.urls import path

from apps.accounts.owner_views import instructor_management, revoke_invitation

app_name = "owner-accounts"
urlpatterns = [
    path("instructors/", instructor_management, name="instructors"),
    path("invitations/<int:invitation_id>/revoke/", revoke_invitation, name="revoke-invitation"),
]
