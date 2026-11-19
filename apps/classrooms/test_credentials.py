from unittest.mock import patch

from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import StudentProfile
from apps.classrooms.credential_services import reset_student_credentials
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True, SESSION_ENGINE="django.contrib.sessions.backends.db")
class StudentCredentialTests(TestCase):
    old = "Synthetic-Previous-Password!4321"
    new = "Synthetic-Reissued-Password!8735"

    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.user("owner", "OWNER")
        self.teacher = self.user("teacher", "INSTRUCTOR")
        self.unassigned = self.user("unassigned", "INSTRUCTOR")
        self.student = self.user("learner", "STUDENT")
        self.room = Classroom.objects.create(organization=self.org, name="Robotics", created_by=self.owner)
        self.extra = Classroom.objects.create(organization=self.org, name="Unassigned", created_by=self.owner)
        ClassInstructor.objects.create(classroom=self.room, instructor=self.teacher)
        ClassEnrollment.objects.create(classroom=self.room, student=self.student)
        self.url = reverse("classrooms:student-credentials", args=[self.room.pk, self.student.pk])

    def user(self, username, role):
        user = get_user_model().objects.create_user(
            username=username, email=username + "@example.test" if role != "STUDENT" else "",
            role=role, organization=self.org, password=self.old,
        )
        user.is_verified = lambda: True
        if role == "STUDENT":
            StudentProfile.objects.create(user=user, grade="4")
        return user

    def issue(self, actor=None, **kwargs):
        data = dict(actor=actor or self.teacher, classroom_id=self.room.pk, student_id=self.student.pk)
        data.update(kwargs)
        return reset_student_credentials(**data)

    def login(self, client=None, user=None):
        client = client or self.client
        user = user or self.teacher
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def db_session(self, user):
        session = SessionStore()
        session[SESSION_KEY] = str(user.pk)
        session.save()
        return session.session_key

    def assert_old(self):
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password(self.old))

    def test_reset_hashes_new_password_and_does_not_expose_in_repr(self):
        with patch("apps.classrooms.credential_services.secrets.token_urlsafe", return_value=self.new):
            credentials = self.issue()
        self.student.refresh_from_db()
        self.assertFalse(self.student.check_password(self.old))
        self.assertTrue(self.student.check_password(self.new))
        self.assertNotEqual(self.student.password, self.new)
        self.assertEqual(credentials.username, self.student.username)
        self.assertEqual(credentials.password, self.new)
        self.assertNotIn(self.new, repr(credentials))
        self.assertEqual(self.student.role, "STUDENT")
        self.assertFalse(self.student.is_staff)

    def test_repeated_reset_replaces_prior_issued_password(self):
        first = self.issue()
        second = self.issue()
        self.assertNotEqual(first.password, second.password)
        self.student.refresh_from_db()
        self.assertFalse(self.student.check_password(first.password))
        self.assertTrue(self.student.check_password(second.password))

    def test_owner_allowed_and_staff_target_denied(self):
        self.issue(self.owner)
        owner_hash = self.owner.password
        with self.assertRaises(PermissionDenied):
            self.issue(self.owner, student_id=self.owner.pk)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.password, owner_hash)

    def test_unassigned_removed_and_unenrolled_denied(self):
        with self.assertRaises(PermissionDenied):
            self.issue(self.unassigned)
        ClassInstructor.objects.filter(instructor=self.teacher).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.issue()
        ClassEnrollment.objects.filter(student=self.student).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.issue(self.owner)
        self.assert_old()

    def test_archived_and_foreign_target_denied(self):
        with self.assertRaises(PermissionDenied):
            self.issue(classroom_id=self.extra.pk)
        get_user_model().objects.filter(pk=self.student.pk).update(organization=self.other)
        with self.assertRaises(PermissionDenied):
            self.issue(self.owner)
        get_user_model().objects.filter(pk=self.student.pk).update(organization=self.org)
        Classroom.objects.filter(pk=self.room.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.issue(self.owner)
        self.assert_old()

    def test_inactive_target_actor_and_mfa_denied(self):
        get_user_model().objects.filter(pk=self.student.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.issue()
        get_user_model().objects.filter(pk=self.student.pk).update(is_active=True)
        get_user_model().objects.filter(pk=self.teacher.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.issue()
        self.owner.is_verified = lambda: False
        with self.assertRaises(PermissionDenied):
            self.issue(self.owner)
        self.assert_old()

    def test_target_sessions_revoked_other_sessions_preserved(self):
        keys = [self.db_session(self.student), self.db_session(self.student)]
        owner_key = self.db_session(self.owner)
        self.issue()
        self.assertFalse(Session.objects.filter(session_key__in=keys).exists())
        self.assertTrue(Session.objects.filter(session_key=owner_key).exists())

    def test_cleanup_failure_rolls_back_password_and_preserves_session(self):
        key = self.db_session(self.student)
        with patch("apps.classrooms.credential_services.Session.objects.filter", side_effect=RuntimeError("synthetic")):
            with self.assertRaises(RuntimeError):
                self.issue()
        self.assert_old()
        self.assertTrue(Session.objects.filter(session_key=key).exists())

    @override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
    def test_unsupported_session_engine_rejected(self):
        with self.assertRaises(ValidationError):
            self.issue()
        self.assert_old()

    def test_password_policy_failure_does_not_modify_account(self):
        with patch("apps.classrooms.credential_services.validate_password", side_effect=ValidationError("synthetic")):
            with self.assertRaises(ValidationError):
                self.issue()
        self.assert_old()

    def test_get_is_read_only_and_has_privacy_headers(self):
        self.login()
        response = self.client.get(self.url)
        self.assertContains(response, self.student.username)
        self.assertNotContains(response, self.old)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertIn("noindex", response["X-Robots-Tag"])
        self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assert_old()

    def test_confirmation_required(self):
        self.login()
        self.assertEqual(self.client.post(self.url, {}).status_code, 400)
        self.assert_old()

    def test_post_displays_secret_without_persisting_or_retrieving_on_get(self):
        self.login()
        with patch("apps.classrooms.credential_services.secrets.token_urlsafe", return_value=self.new):
            response = self.client.post(self.url, {"confirm": "on"})
        self.assertContains(response, self.new)
        self.assertNotIn("Location", response)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn(self.new, str(dict(self.client.session)))
        self.assertNotIn(self.new, str(response.cookies))
        self.assertEqual(str(self.client.session[SESSION_KEY]), str(self.teacher.pk))
        self.assertNotContains(self.client.get(self.url), self.new)
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password(self.new))

    def test_unassigned_and_nonstudent_urls_hidden(self):
        self.login(user=self.unassigned)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.post(self.url, {"confirm": "on"}).status_code, 404)

    def test_csrf_origin_checks(self):
        client = Client(enforce_csrf_checks=True)
        self.login(client)
        self.assertEqual(client.post(self.url, {"confirm": "on"}).status_code, 403)
        self.assertEqual(client.get(self.url).status_code, 200)
        data = {"confirm": "on", "csrfmiddlewaretoken": client.cookies["csrftoken"].value}
        for origin in ("null", "https://attacker.example"):
            self.assertEqual(client.post(self.url, data, HTTP_ORIGIN=origin).status_code, 403)
        self.assert_old()
        self.assertEqual(client.post(self.url, data, HTTP_ORIGIN="http://testserver").status_code, 200)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_disabled_gate(self):
        with self.assertRaises(PermissionDenied):
            self.issue()
        self.login()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_unverified_and_anonymous_redirect(self):
        client = Client()
        client.force_login(self.owner)
        self.assertEqual(client.get(self.url).status_code, 302)
        self.assertEqual(Client().get(self.url).status_code, 302)
