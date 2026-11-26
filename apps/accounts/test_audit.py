import json
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts import audit, throttle
from apps.accounts.audit_models import AuditEvent, AuditEventType
from apps.accounts.models import StudentProfile
from apps.classrooms.credential_services import reset_student_credentials
from apps.classrooms.models import ClassEnrollment, Classroom
from apps.classrooms.services import end_enrollment, enroll_student
from apps.classrooms.student_services import create_student_in_class
from apps.organizations.models import Organization

PASSWORD = "Synthetic-Previous-Password!4321"


def events(event_type=None):
    queryset = AuditEvent.objects.all()
    return queryset.filter(event_type=event_type) if event_type else queryset


def everything_stored():
    return json.dumps(list(AuditEvent.objects.values()), default=str).lower()


class AuditBase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.org = Organization.objects.create(name="Synthetic center")
        self.other_org = Organization.objects.create(name="Other center")
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", role="OWNER",
            organization=self.org, password=PASSWORD,
        )
        self.owner.is_verified = lambda: True
        self.instructor = User.objects.create_user(
            username="teacher", email="teacher@example.test", role="INSTRUCTOR",
            organization=self.org, password=PASSWORD,
        )
        self.instructor.is_verified = lambda: True
        self.student = self.make_student("learner")
        self.second = self.make_student("classmate")
        self.room = Classroom.objects.create(organization=self.org, name="Robotics", created_by=self.owner)
        ClassEnrollment.objects.create(classroom=self.room, student=self.student)

    def make_student(self, name, org=None):
        student = get_user_model().objects.create_user(
            username=name, email="", role="STUDENT",
            organization=org or self.org, password=PASSWORD,
        )
        StudentProfile.objects.create(user=student, grade="4")
        return student


class AuditRecordTests(AuditBase):
    def test_unknown_event_type_is_refused(self):
        with self.assertRaises(ValueError):
            audit.record("NOT_AN_EVENT")

    def test_detail_keys_are_allowlisted(self):
        with self.assertRaises(ValueError):
            audit.record(AuditEventType.ENROLLED, detail={"password": "x"})
        self.assertFalse(events().exists())

    def test_long_or_non_text_detail_values_are_refused(self):
        with self.assertRaises(ValueError):
            audit.record(AuditEventType.ENROLLED, detail={"classroom_name": "x" * 151})
        with self.assertRaises(ValueError):
            audit.record(AuditEventType.ENROLLED, detail={"classroom_name": 5})

    def test_saved_events_cannot_be_updated(self):
        event = audit.record(AuditEventType.ENROLLED, actor=self.owner, subject=self.student)
        with self.assertRaises(ValueError):
            event.save()

    def test_actor_subject_and_organization_are_recorded(self):
        event = audit.record(
            AuditEventType.ENROLLED, actor=self.owner, subject=self.student, classroom_id=self.room.pk,
        )
        self.assertEqual(event.organization_id, self.org.pk)
        self.assertEqual((event.actor_username, event.subject_username), ("owner", "learner"))
        self.assertEqual(event.classroom_id, self.room.pk)

    def test_database_constraint_rejects_unknown_types(self):
        with self.assertRaises(ValidationError):
            AuditEvent(event_type="NOT_AN_EVENT").full_clean()


@override_settings(LMS_STUDENT_AUTH_ENABLED=True, LMS_STAFF_AUTH_ENABLED=True)
class SignInAuditTests(AuditBase):
    def student_post(self, name, password):
        return self.client.post(reverse("student-login"), {"student_username": name, "password": password})

    def staff_post(self, email, password):
        url = reverse("two_factor:login")
        prefix = self.client.get(url).context["wizard"]["management_form"].prefix
        return self.client.post(url, {
            f"{prefix}-current_step": "auth", "auth-username": email, "auth-password": password,
        })

    def test_student_sign_in_is_recorded(self):
        self.assertEqual(self.student_post("learner", PASSWORD).status_code, 302)
        event = events(AuditEventType.SIGN_IN_SUCCESS).get()
        self.assertEqual(event.actor_id, self.student.pk)
        self.assertEqual(event.organization_id, self.org.pk)
        self.assertEqual(event.detail, {"role": "STUDENT"})

    def test_only_the_first_failure_in_a_window_is_recorded(self):
        for _ in range(3):
            self.assertEqual(self.student_post("learner", "wrong").status_code, 400)
        event = events(AuditEventType.SIGN_IN_FAILED).get()
        self.assertEqual(event.subject_id, self.student.pk)
        self.assertEqual(event.organization_id, self.org.pk)
        self.assertEqual(len(event.detail["name_digest"]), 16)
        self.assertEqual(set(event.detail), {"name_digest"})

    def test_lockout_is_recorded_once_and_later_attempts_are_not(self):
        for _ in range(throttle.MAX_FAILURES):
            self.student_post("learner", "wrong")
        self.assertEqual(events(AuditEventType.SIGN_IN_FAILED).count(), 1)
        self.assertEqual(events(AuditEventType.SIGN_IN_LOCKED).count(), 1)
        before = events().count()
        self.assertEqual(self.student_post("learner", PASSWORD).status_code, 429)
        self.assertEqual(events().count(), before)

    def test_unknown_names_have_no_account_organization_or_typed_name(self):
        self.student_post("Nobody-Here", "wrong")
        event = events(AuditEventType.SIGN_IN_FAILED).get()
        self.assertIsNone(event.subject_id)
        self.assertIsNone(event.organization_id)
        self.assertEqual(event.subject_username, "")
        self.assertNotIn("nobody-here", everything_stored())

    def test_typed_password_is_never_stored(self):
        self.student_post("learner", "Typed-Secret-Value-77!")
        self.assertTrue(events().exists())
        self.assertNotIn("typed-secret-value-77", everything_stored())

    def test_staff_first_failure_is_recorded_once(self):
        for _ in range(2):
            self.assertEqual(self.staff_post(self.owner.email, "wrong").status_code, 200)
        event = events(AuditEventType.SIGN_IN_FAILED).get()
        self.assertEqual(event.subject_id, self.owner.pk)
        self.assertEqual(event.organization_id, self.org.pk)
        self.assertNotIn(self.owner.email, json.dumps(event.detail))

    def test_staff_login_with_unknown_email_has_no_organization(self):
        self.staff_post("nobody@example.test", "wrong")
        event = events(AuditEventType.SIGN_IN_FAILED).get()
        self.assertIsNone(event.organization_id)
        self.assertNotIn("nobody@example.test", everything_stored())


class ServiceAuditTests(AuditBase):
    def test_credential_reset_is_recorded_without_the_password(self):
        credentials = reset_student_credentials(
            actor=self.owner, classroom_id=self.room.pk, student_id=self.student.pk,
        )
        event = events(AuditEventType.CREDENTIAL_RESET).get()
        self.assertEqual((event.actor_username, event.subject_username), ("owner", "learner"))
        self.assertEqual(event.classroom_id, self.room.pk)
        self.assertEqual(event.detail, {"classroom_name": "Robotics"})
        self.assertNotIn(credentials.password.lower(), everything_stored())

    def test_denied_credential_reset_records_nothing(self):
        with self.assertRaises(PermissionDenied):
            reset_student_credentials(
                actor=self.instructor, classroom_id=self.room.pk, student_id=self.student.pk,
            )
        self.assertFalse(events().exists())

    def test_enrollment_is_recorded_once(self):
        for _ in range(2):
            enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.second.pk)
        event = events(AuditEventType.ENROLLED).get()
        self.assertEqual((event.actor_username, event.subject_username), ("owner", "classmate"))
        self.assertEqual(event.detail, {"classroom_name": "Robotics"})

    def test_ending_enrollment_is_recorded_once(self):
        for _ in range(2):
            end_enrollment(actor=self.owner, classroom_id=self.room.pk, student_id=self.student.pk)
        event = events(AuditEventType.ENROLLMENT_ENDED).get()
        self.assertEqual(event.subject_username, "learner")

    def test_ending_an_enrollment_that_never_existed_records_nothing(self):
        end_enrollment(actor=self.owner, classroom_id=self.room.pk, student_id=self.second.pk)
        self.assertFalse(events().exists())

    def test_failed_audit_write_rolls_back_the_enrollment(self):
        with patch("apps.classrooms.services.audit.record", side_effect=ValueError):
            with self.assertRaises(ValueError):
                enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.second.pk)
        self.assertFalse(ClassEnrollment.objects.filter(classroom=self.room, student=self.second).exists())

    def test_student_creation_is_recorded_without_the_password(self):
        password = "Synthetic-New-Student-Pass!5280"
        student = create_student_in_class(
            actor=self.owner, classroom_id=self.room.pk, username="newkid",
            display_name="New Kid", grade="4", password=password,
        )
        event = events().get()
        self.assertEqual(event.event_type, AuditEventType.STUDENT_CREATED)
        self.assertEqual((event.subject_id, event.classroom_id), (student.pk, self.room.pk))
        self.assertNotIn(password.lower(), everything_stored())

    def test_failed_student_creation_records_nothing(self):
        with self.assertRaises(ValidationError):
            create_student_in_class(
                actor=self.owner, classroom_id=self.room.pk, username="learner",
                display_name="Copy", grade="4", password="Synthetic-New-Student-Pass!5280",
            )
        self.assertFalse(events().exists())


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class AuditPageTests(AuditBase):
    def setUp(self):
        super().setUp()
        self.url = reverse("owner-accounts:audit-log")
        self.elsewhere = self.make_student("elsewhere-kid", org=self.other_org)

    def login_verified(self, user=None):
        user = user or self.owner
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        self.client.force_login(user)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def test_owner_sees_only_own_organization(self):
        audit.record(AuditEventType.ENROLLED, actor=self.owner, subject=self.student)
        audit.record(AuditEventType.ENROLLED, subject=self.elsewhere)
        self.login_verified()
        response = self.client.get(self.url)
        self.assertContains(response, "learner")
        self.assertNotContains(response, "elsewhere-kid")
        self.assertIn("no-store", response["Cache-Control"])

    def test_instructor_is_denied(self):
        self.login_verified(self.instructor)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_anonymous_user_redirects_to_login(self):
        self.assertRedirects(self.client.get(self.url), reverse("two_factor:login"),
                             fetch_redirect_response=False)

    def test_page_is_read_only(self):
        self.login_verified()
        self.assertEqual(self.client.post(self.url, {}).status_code, 405)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_feature_gate_blocks_the_page(self):
        self.login_verified()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_type_filter_and_invalid_filter(self):
        audit.record(AuditEventType.ENROLLED, actor=self.owner, subject=self.student)
        audit.record(AuditEventType.ENROLLMENT_ENDED, actor=self.owner, subject=self.student)
        self.login_verified()
        shown = self.client.get(self.url, {"type": "ENROLLED"}).context["page"]
        self.assertEqual({event.event_type for event in shown}, {"ENROLLED"})
        response = self.client.get(self.url, {"type": "NOT_AN_EVENT"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected"], "")

    def test_paging_is_bounded(self):
        AuditEvent.objects.bulk_create(
            AuditEvent(event_type="ENROLLED", organization=self.org) for _ in range(51)
        )
        self.login_verified()
        page = self.client.get(self.url, {"type": "ENROLLED"}).context["page"]
        self.assertEqual(len(page), 50)
        self.assertEqual(page.paginator.count, 51)

    def test_values_are_escaped(self):
        audit.record(
            AuditEventType.ENROLLED, actor=self.owner, subject=self.student,
            detail={"classroom_name": "<b>x</b>"},
        )
        self.login_verified()
        response = self.client.get(self.url)
        self.assertNotContains(response, "<b>x</b>")
        self.assertContains(response, "&lt;b&gt;x&lt;/b&gt;")


class RetentionTests(AuditBase):
    def aged(self, days):
        event = audit.record(AuditEventType.ENROLLED, actor=self.owner, subject=self.student)
        AuditEvent.objects.filter(pk=event.pk).update(created_at=timezone.now() - timedelta(days=days))
        return event

    def test_purge_removes_only_events_past_the_default_90_days(self):
        old, recent = self.aged(91), self.aged(89)
        self.assertEqual(audit.purge_expired(), 1)
        self.assertEqual(list(events().values_list("pk", flat=True)), [recent.pk])
        self.assertFalse(AuditEvent.objects.filter(pk=old.pk).exists())

    @override_settings(LMS_AUDIT_RETENTION_DAYS=30)
    def test_retention_period_is_configurable(self):
        self.aged(31)
        self.aged(29)
        self.assertEqual(audit.purge_expired(), 1)

    def test_invalid_retention_settings_are_refused(self):
        for value in (0, -1, True, "90", 3651):
            with self.subTest(value=value), override_settings(LMS_AUDIT_RETENTION_DAYS=value):
                with self.assertRaises(ImproperlyConfigured):
                    audit.retention_days()

    def test_management_command_reports_the_count(self):
        self.aged(120)
        out = StringIO()
        call_command("purge_audit_events", stdout=out)
        self.assertIn("Deleted 1 audit event(s) older than 90 days.", out.getvalue())
        self.assertFalse(events().exists())
