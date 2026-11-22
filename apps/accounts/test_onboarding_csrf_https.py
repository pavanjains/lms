import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts import test_onboarding as foundation
from apps.accounts.models import InstructorInvitation


@override_settings(
    DEBUG=False, ALLOWED_HOSTS=["testserver"], SECURE_SSL_REDIRECT=True,
    SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True, CSRF_TRUSTED_ORIGINS=[],
    LMS_STAFF_AUTH_ENABLED=True, LMS_INSTRUCTOR_ONBOARDING_ENABLED=True,
    LMS_PUBLIC_ORIGIN="https://testserver", LMS_INVITATION_FROM_EMAIL="owner@example.test",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class OnboardingHttpsCsrfTests(TestCase):
    setUp = foundation.OnboardingTests.setUp
    activation_data = foundation.OnboardingTests.activation_data
    csrf_client = foundation.OnboardingTests.csrf_client
    password = foundation.OnboardingTests.password

    def issue(self):
        response = self.client.post(self.invite_url, {
            "email": "new@example.test", "confirm": "on",
        }, secure=True)
        self.assertEqual(response.status_code, 200)
        token = re.search(r"/onboarding/activate/([A-Za-z0-9_-]+)/", mail.outbox[-1].body).group(1)
        return InstructorInvitation.objects.latest("pk"), token

    def form(self, client, url, data):
        response = client.get(url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        return {**data, "csrfmiddlewaretoken": client.cookies["csrftoken"].value}

    def post(self, client, url, data, **headers):
        return client.post(url, data, secure=True, **headers)

    def test_https_activation_accepts_same_origin_referer_without_origin(self):
        invitation, token = self.issue()
        url = reverse("onboarding:activate", args=[token])
        client = self.csrf_client(owner=False)
        data = self.form(client, url, self.activation_data())
        response = self.post(client, url, data, HTTP_REFERER="https://testserver" + url)
        self.assertRedirects(response, reverse("onboarding:complete"), fetch_redirect_response=False)
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.accepted_at)
        user = get_user_model().objects.get(username="newteacher")
        self.assertEqual(user.role, "INSTRUCTOR")
        self.assertEqual(user.organization_id, self.organization.pk)
        self.assertNotIn("_auth_user_id", client.session)
        self.assertEqual(client.get(url, secure=True).status_code, 400)

    def test_https_activation_accepts_same_origin_origin_without_referer(self):
        invitation, token = self.issue()
        url = reverse("onboarding:activate", args=[token])
        client = self.csrf_client(owner=False)
        data = self.form(client, url, self.activation_data())
        response = self.post(client, url, data, HTTP_ORIGIN="https://testserver")
        self.assertRedirects(response, reverse("onboarding:complete"), fetch_redirect_response=False)
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.accepted_at)
        self.assertNotIn("_auth_user_id", client.session)

    def test_https_invite_accepts_same_origin_referer_without_origin(self):
        client = self.csrf_client(owner=True)
        data = self.form(client, self.invite_url, {"email": "new@example.test", "confirm": "on"})
        response = self.post(client, self.invite_url, data,
                             HTTP_REFERER="https://testserver" + self.invite_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(InstructorInvitation.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_https_resend_accepts_same_origin_referer_without_origin(self):
        invitation, token = self.issue()
        url = reverse("owner-accounts:resend-invitation", args=[invitation.pk])
        client = self.csrf_client(owner=True)
        data = self.form(client, url, {"confirm": "on"})
        response = self.post(client, url, data, HTTP_REFERER="https://testserver" + url)
        self.assertEqual(response.status_code, 200)
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.revoked_at)
        self.assertEqual(InstructorInvitation.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(Client().get(reverse("onboarding:activate", args=[token]), secure=True).status_code, 400)

    def reject_origins(self, client, url, data):
        data = self.form(client, url, data)
        for origin in ("null", "https://attacker.example", "http://testserver", "https://testserver:8443"):
            with self.subTest(origin=origin):
                response = self.post(client, url, data, HTTP_ORIGIN=origin,
                                     HTTP_REFERER="https://testserver" + url)
                self.assertEqual(response.status_code, 403)
                self.assertIn("no-store", response["Cache-Control"])

    def test_https_invite_rejects_null_foreign_scheme_and_port_origins(self):
        self.reject_origins(self.csrf_client(owner=True), self.invite_url,
                            {"email": "new@example.test", "confirm": "on"})
        self.assertFalse(InstructorInvitation.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_https_resend_rejects_null_foreign_scheme_and_port_origins(self):
        invitation, _ = self.issue()
        url = reverse("owner-accounts:resend-invitation", args=[invitation.pk])
        self.reject_origins(self.csrf_client(owner=True), url, {"confirm": "on"})
        invitation.refresh_from_db()
        self.assertIsNone(invitation.revoked_at)
        self.assertEqual(InstructorInvitation.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_https_activation_rejects_null_foreign_scheme_and_port_origins(self):
        invitation, token = self.issue()
        url = reverse("onboarding:activate", args=[token])
        self.reject_origins(self.csrf_client(owner=False), url, self.activation_data())
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_at)
        self.assertFalse(get_user_model().objects.filter(username="newteacher").exists())

    def endpoints(self, invitation, token):
        return [
            (True, self.invite_url, {"email": "other@example.test", "confirm": "on"}),
            (True, reverse("owner-accounts:resend-invitation", args=[invitation.pk]), {"confirm": "on"}),
            (False, reverse("onboarding:activate", args=[token]), self.activation_data()),
        ]

    def assert_unchanged(self, invitation):
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_at)
        self.assertIsNone(invitation.revoked_at)
        self.assertEqual(InstructorInvitation.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(get_user_model().objects.filter(username="newteacher").exists())

    def test_https_without_origin_rejects_missing_insecure_foreign_or_malformed_referer(self):
        invitation, token = self.issue()
        for owner, url, data in self.endpoints(invitation, token):
            client = self.csrf_client(owner=owner)
            data = self.form(client, url, data)
            for headers in ({}, {"HTTP_REFERER": "http://testserver" + url},
                            {"HTTP_REFERER": "https://attacker.example/"},
                            {"HTTP_REFERER": "not-a-url"}):
                with self.subTest(owner=owner, endpoint=url.split("/")[1:3], headers=bool(headers)):
                    self.assertEqual(self.post(client, url, data, **headers).status_code, 403)
        self.assert_unchanged(invitation)

    def test_https_valid_origin_does_not_bypass_missing_csrf_token(self):
        invitation, token = self.issue()
        for owner, url, data in self.endpoints(invitation, token):
            client = self.csrf_client(owner=owner)
            self.form(client, url, data)
            response = self.post(client, url, data, HTTP_ORIGIN="https://testserver")
            self.assertEqual(response.status_code, 403)
        self.assert_unchanged(invitation)

    def test_https_validation_and_unavailable_pages_keep_privacy_headers(self):
        invitation, token = self.issue()
        url = reverse("onboarding:activate", args=[token])
        client = self.csrf_client(owner=False)
        data = self.form(client, url, self.activation_data(password2="mismatch"))
        response = self.post(client, url, data, HTTP_ORIGIN="https://testserver")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotContains(response, self.password, status_code=400)
        self.assertNotContains(response, token, status_code=400)
        self.assert_unchanged(invitation)
        for changes in ({"expires_at": timezone.now() - timedelta(seconds=1)},
                        {"expires_at": timezone.now() + timedelta(hours=1), "revoked_at": timezone.now()}):
            InstructorInvitation.objects.filter(pk=invitation.pk).update(**changes)
            response = client.get(url, secure=True)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response["Referrer-Policy"], "same-origin")
            self.assertIn("no-store", response["Cache-Control"])
            self.assertNotContains(response, token, status_code=400)
