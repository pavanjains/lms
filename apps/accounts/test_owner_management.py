from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.invitation_services import issue_instructor_invitation
from apps.accounts.models import InstructorInvitation
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class OwnerManagementTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Synthetic Center")
        self.other_org = Organization.objects.create(name="Other Center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", role="OWNER",
            organization=self.organization,
        )
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@example.test", role="INSTRUCTOR",
            organization=self.organization,
        )
        self.other_teacher = User.objects.create_user(
            username="other-teacher", email="private@example.test", role="INSTRUCTOR",
            organization=self.other_org,
        )
        with patch.object(self.owner, "is_verified", return_value=True, create=True):
            self.invitation, self.token = issue_instructor_invitation(
                actor=self.owner, email="pending@example.test",
            )
        self.list_url = reverse("owner-accounts:instructors")
        self.revoke_url = reverse("owner-accounts:revoke-invitation", args=[self.invitation.pk])

    def login_verified(self, user=None, client=None):
        user = user or self.owner
        client = client or self.client
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def test_owner_sees_only_own_organization(self):
        self.login_verified()
        response = self.client.get(self.list_url)
        self.assertContains(response, self.teacher.email)
        self.assertContains(response, self.invitation.email)
        self.assertNotContains(response, self.other_teacher.email)
        self.assertIn("no-store", response["Cache-Control"])

    def test_listing_never_renders_invitation_secrets(self):
        self.login_verified()
        response = self.client.get(self.list_url)
        self.assertNotContains(response, self.token)
        self.assertNotContains(response, self.invitation.token_digest)

    def test_verified_instructor_is_denied(self):
        self.login_verified(self.teacher)
        self.assertEqual(self.client.get(self.list_url).status_code, 403)
        self.assertEqual(self.client.post(self.revoke_url, {"confirm": "on"}).status_code, 403)

    def test_unverified_owner_redirects_to_login(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.list_url)
        self.assertRedirects(response, reverse("two_factor:login"), fetch_redirect_response=False)

    def test_anonymous_user_redirects_to_login(self):
        self.assertRedirects(self.client.get(self.list_url), reverse("two_factor:login"),
                             fetch_redirect_response=False)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_feature_gate_blocks_owner_ui(self):
        self.login_verified()
        self.assertEqual(self.client.get(self.list_url).status_code, 404)

    def test_get_confirmation_does_not_revoke(self):
        self.login_verified()
        self.assertEqual(self.client.get(self.revoke_url).status_code, 200)
        self.invitation.refresh_from_db()
        self.assertIsNone(self.invitation.revoked_at)

    def test_post_requires_confirmation(self):
        self.login_verified()
        self.assertEqual(self.client.post(self.revoke_url, {}).status_code, 400)
        self.invitation.refresh_from_db()
        self.assertIsNone(self.invitation.revoked_at)

    def test_confirmed_post_revokes(self):
        self.login_verified()
        response = self.client.post(self.revoke_url, {"confirm": "on"})
        self.assertRedirects(response, self.list_url, fetch_redirect_response=False)
        self.invitation.refresh_from_db()
        self.assertIsNotNone(self.invitation.revoked_at)

    def test_cross_organization_invitation_is_hidden(self):
        self.login_verified()
        self.invitation.organization = self.other_org
        self.invitation.save(update_fields=["organization"])
        self.assertEqual(self.client.get(self.revoke_url).status_code, 404)
        self.assertEqual(self.client.post(self.revoke_url, {"confirm": "on"}).status_code, 404)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        self.login_verified(client=client)
        self.assertEqual(client.post(self.revoke_url, {"confirm": "on"}).status_code, 403)
        self.invitation.refresh_from_db()
        self.assertIsNone(self.invitation.revoked_at)

    def test_accepted_invitation_has_conflict_response(self):
        self.login_verified()
        self.invitation.accepted_at = timezone.now()
        self.invitation.accepted_user = self.teacher
        self.invitation.save(update_fields=["accepted_at", "accepted_user"])
        self.assertEqual(self.client.post(self.revoke_url, {"confirm": "on"}).status_code, 409)

    def test_search_and_empty_state(self):
        self.login_verified()
        response = self.client.get(self.list_url, {"q": "no-match"})
        self.assertContains(response, "No instructor accounts match.")
        self.assertContains(response, "No invitations match.")

    def test_pagination_is_bounded(self):
        self.login_verified()
        User = get_user_model()
        for index in range(26):
            User.objects.create_user(
                username=f"teacher-{index:02}", email=f"teacher-{index}@example.test",
                role="INSTRUCTOR", organization=self.organization,
            )
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.context["instructor_page"]), 25)
        self.assertEqual(response.context["instructor_page"].paginator.count, 27)

    def test_expired_status_is_displayed(self):
        self.login_verified()
        InstructorInvitation.objects.filter(pk=self.invitation.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        self.assertContains(self.client.get(self.list_url), "Expired")
