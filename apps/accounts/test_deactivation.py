from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.deactivation import deactivate_instructor
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True, SESSION_ENGINE="django.contrib.sessions.backends.db")
class DeactivationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Synthetic Center")
        self.other = Organization.objects.create(name="Other Center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", role="OWNER", organization=self.organization,
        )
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@example.test", role="INSTRUCTOR",
            organization=self.organization, password="Synthetic-Password-9371!",
        )
        self.student = User.objects.create_user(
            username="student", role="STUDENT", organization=self.organization,
        )
        self.foreign = User.objects.create_user(
            username="foreign", email="foreign@example.test", role="INSTRUCTOR", organization=self.other,
        )
        self.url = reverse("owner-accounts:deactivate-instructor", args=[self.teacher.pk])
        self.list_url = reverse("owner-accounts:instructors")
        self.verified(self.owner, self.client)

    def verified(self, user, client):
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        return session.session_key

    def test_get_is_read_only_and_private(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.teacher.email)
        self.assertIn("no-store", response["Cache-Control"])
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    def test_post_requires_confirmation(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, 400)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    def test_confirmed_post_preserves_account_and_credentials(self):
        password = self.teacher.password
        count = get_user_model().objects.count()
        response = self.client.post(self.url, {"confirm": "on"})
        self.assertRedirects(response, self.list_url, fetch_redirect_response=False)
        self.teacher.refresh_from_db()
        self.assertFalse(self.teacher.is_active)
        self.assertEqual(self.teacher.password, password)
        self.assertEqual(self.teacher.role, "INSTRUCTOR")
        self.assertEqual(get_user_model().objects.count(), count)

    def test_all_target_sessions_revoked_and_access_denied(self):
        first, second = Client(), Client()
        keys = [self.verified(self.teacher, first), self.verified(self.teacher, second)]
        owner_key = self.client.session.session_key
        self.assertEqual(first.get(reverse("staff-home")).status_code, 200)
        self.client.post(self.url, {"confirm": "on"})
        self.assertFalse(Session.objects.filter(session_key__in=keys).exists())
        self.assertTrue(Session.objects.filter(session_key=owner_key).exists())
        self.assertTrue(TOTPDevice.objects.filter(user=self.teacher).exists())
        self.assertRedirects(first.get(reverse("staff-home")), reverse("two_factor:login"),
                             fetch_redirect_response=False)
        self.assertIsNone(authenticate(username=self.teacher.email, password="Synthetic-Password-9371!"))

    def test_repeat_is_safe(self):
        for _ in range(2):
            self.assertEqual(self.client.post(self.url, {"confirm": "on"}).status_code, 302)
        self.teacher.refresh_from_db()
        self.assertFalse(self.teacher.is_active)

    def test_other_roles_and_organization_hidden(self):
        for user in (self.owner, self.student, self.foreign):
            with self.subTest(user=user.username):
                url = reverse("owner-accounts:deactivate-instructor", args=[user.pk])
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 404)
                user.refresh_from_db()
                self.assertTrue(user.is_active)

    def test_instructor_cannot_manage_instructors(self):
        self.verified(self.teacher, self.client)
        self.assertEqual(self.client.post(self.url, {"confirm": "on"}).status_code, 403)

    def test_unverified_owner_is_redirected(self):
        client = Client()
        client.force_login(self.owner)
        self.assertRedirects(client.get(self.url), reverse("two_factor:login"),
                             fetch_redirect_response=False)

    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        self.verified(self.owner, client)
        self.assertEqual(client.post(self.url, {"confirm": "on"}).status_code, 403)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_feature_gate_stays_closed(self):
        self.assertEqual(self.client.post(self.url, {"confirm": "on"}).status_code, 404)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    def test_service_rechecks_owner_from_database(self):
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with patch.object(self.owner, "is_verified", return_value=True, create=True):
            with self.assertRaises(PermissionDenied):
                deactivate_instructor(actor=self.owner, instructor_id=self.teacher.pk)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    @override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
    def test_service_rejects_unsupported_session_backend(self):
        with patch.object(self.owner, "is_verified", return_value=True, create=True):
            with self.assertRaises(ValidationError):
                deactivate_instructor(actor=self.owner, instructor_id=self.teacher.pk)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    def test_session_cleanup_failure_rolls_back_deactivation(self):
        with patch.object(self.owner, "is_verified", return_value=True, create=True):
            with patch("apps.accounts.deactivation.Session.objects.filter", side_effect=RuntimeError("failure")):
                with self.assertRaises(RuntimeError):
                    deactivate_instructor(actor=self.owner, instructor_id=self.teacher.pk)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.is_active)

    def test_service_rejects_non_instructor_and_foreign_targets(self):
        with patch.object(self.owner, "is_verified", return_value=True, create=True):
            for user in (self.owner, self.student, self.foreign):
                with self.subTest(user=user.username):
                    with self.assertRaises(PermissionDenied):
                        deactivate_instructor(actor=self.owner, instructor_id=user.pk)
