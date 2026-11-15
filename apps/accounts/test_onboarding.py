import re
from datetime import timedelta
from smtplib import SMTPException
from unittest.mock import patch

from django.contrib import mail
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import InstructorInvitation
from apps.organizations.models import Organization


@override_settings(
    LMS_STAFF_AUTH_ENABLED=True, LMS_INSTRUCTOR_ONBOARDING_ENABLED=True,
    LMS_PUBLIC_ORIGIN="https://center.example.test", LMS_INVITATION_FROM_EMAIL="owner@example.test",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class OnboardingTests(TestCase):
    password = "Synthetic-Onboarding-Password!13792"

    def setUp(self):
        self.organization = Organization.objects.create(name="Synthetic Center")
        self.owner = get_user_model().objects.create_user(
            username="owner", email="owner@example.test", role="OWNER", organization=self.organization,
        )
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        self.client.force_login(self.owner)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        self.invite_url = reverse("owner-accounts:invite")

    def issue(self):
        response = self.client.post(self.invite_url, {"email": "new@example.test", "confirm": "on"})
        self.assertEqual(response.status_code, 200)
        token = re.search(r"/onboarding/activate/([A-Za-z0-9_-]+)/", mail.outbox[-1].body).group(1)
        return InstructorInvitation.objects.latest("pk"), token

    def activation_data(self, **overrides):
        data = {"username": "newteacher", "password1": self.password, "password2": self.password}
        data.update(overrides)
        return data

    def test_owner_invites_without_exposing_token_in_response(self):
        invitation, token = self.issue()
        self.assertEqual(mail.outbox[-1].to, ["new@example.test"])
        self.assertNotIn(token, self.client.get(self.invite_url).content.decode())
        self.assertNotEqual(token, invitation.token_digest)

    def test_get_invite_has_no_side_effect(self):
        self.assertEqual(self.client.get(self.invite_url).status_code, 200)
        self.assertFalse(InstructorInvitation.objects.exists())

    def test_confirmation_required(self):
        self.assertEqual(self.client.post(self.invite_url, {"email": "new@example.test"}).status_code, 400)
        self.assertFalse(InstructorInvitation.objects.exists())

    def test_resend_rotates_token(self):
        old, token = self.issue()
        url = reverse("owner-accounts:resend-invitation", args=[old.pk])
        self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 200)
        old.refresh_from_db()
        self.assertIsNotNone(old.revoked_at)
        self.assertNotIn(token, mail.outbox[-1].body)

    def test_activation_does_not_sign_in_and_ignores_role_injection(self):
        invitation, token = self.issue()
        client = Client()
        url = reverse("onboarding:activate", args=[token])
        self.assertEqual(client.get(url).status_code, 200)
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_at)
        response = client.post(url, self.activation_data(role="OWNER", organization="forged"))
        self.assertRedirects(response, reverse("onboarding:complete"), fetch_redirect_response=False)
        user = get_user_model().objects.get(username="newteacher")
        self.assertEqual(user.role, "INSTRUCTOR")
        self.assertEqual(user.organization_id, self.organization.pk)
        self.assertTrue(user.check_password(self.password))
        self.assertNotIn("_auth_user_id", client.session)
        self.assertEqual(client.get(url).status_code, 400)

    def test_password_mismatch_keeps_invitation_unused(self):
        invitation, token = self.issue()
        response = Client().post(reverse("onboarding:activate", args=[token]),
                                 self.activation_data(password2="different"))
        self.assertEqual(response.status_code, 400)
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_at)

    def test_expired_invitation_is_unavailable(self):
        invitation, token = self.issue()
        invitation.expires_at = timezone.now() - timedelta(seconds=1)
        invitation.save(update_fields=["expires_at"])
        self.assertEqual(Client().get(reverse("onboarding:activate", args=[token])).status_code, 400)

    def test_mail_failure_rolls_back_replacement(self):
        old, _ = self.issue()
        with patch("apps.accounts.onboarding.EmailMessage.send", side_effect=SMTPException("failure")):
            response = self.client.post(reverse("owner-accounts:resend-invitation", args=[old.pk]),
                                        {"confirm": "on"})
        self.assertEqual(response.status_code, 400)
        old.refresh_from_db()
        self.assertIsNone(old.revoked_at)
        self.assertEqual(InstructorInvitation.objects.count(), 1)

    @override_settings(LMS_PUBLIC_ORIGIN="https://attacker.example/path")
    def test_invalid_origin_prevents_delivery(self):
        self.assertEqual(self.client.post(self.invite_url, {
            "email": "new@example.test", "confirm": "on",
        }).status_code, 400)
        self.assertFalse(InstructorInvitation.objects.exists())

    @override_settings(LMS_INSTRUCTOR_ONBOARDING_ENABLED=False)
    def test_disabled_gate(self):
        self.assertEqual(self.client.get(self.invite_url).status_code, 404)
        self.assertEqual(Client().get(reverse("onboarding:activate", args=["x" * 43])).status_code, 404)

    def test_activation_has_privacy_headers(self):
        _, token = self.issue()
        response = Client().get(reverse("onboarding:activate", args=[token]))
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertIn("no-store", response["Cache-Control"])

    def test_activation_requires_csrf(self):
        _, token = self.issue()
        response = Client(enforce_csrf_checks=True).post(
            reverse("onboarding:activate", args=[token]), self.activation_data(),
        )
        self.assertEqual(response.status_code, 403)

    def test_instructor_cannot_issue_invites(self):
        self.owner.role = "INSTRUCTOR"
        self.owner.save(update_fields=["role"])
        self.assertEqual(self.client.get(self.invite_url).status_code, 403)

    def test_other_organization_resend_is_hidden(self):
        invitation, _ = self.issue()
        invitation.organization = Organization.objects.create(name="Other")
        invitation.save(update_fields=["organization"])
        url = reverse("owner-accounts:resend-invitation", args=[invitation.pk])
        self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 404)
