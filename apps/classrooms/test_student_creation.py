from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.backends import StaffEmailBackend
from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.classrooms.policies import visible_students
from apps.classrooms.student_services import create_student_in_class
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class StudentCreationTests(TestCase):
    password = "Synthetic-Student-Password!7429"

    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.staff("owner", "OWNER")
        self.teacher = self.staff("teacher", "INSTRUCTOR")
        self.shared = self.staff("shared", "INSTRUCTOR")
        self.unassigned = self.staff("unassigned", "INSTRUCTOR")
        self.room = Classroom.objects.create(organization=self.org, name="Robotics", created_by=self.owner)
        self.extra = Classroom.objects.create(organization=self.org, name="Other class", created_by=self.owner)
        for instructor in (self.teacher, self.shared):
            ClassInstructor.objects.create(classroom=self.room, instructor=instructor)
        self.url = reverse("classrooms:create-student", args=[self.room.pk])

    def staff(self, name, role):
        user = get_user_model().objects.create_user(username=name, email=name + "@example.test",
                                                    role=role, organization=self.org)
        user.is_verified = lambda: True
        return user

    def create(self, actor=None, **changes):
        data = dict(actor=actor or self.teacher, classroom_id=self.room.pk, username="learner",
                    display_name="Learner One", grade="4", password=self.password)
        data.update(changes)
        return create_student_in_class(**data)

    def payload(self, **changes):
        data = dict(username="learner", display_name="Learner One", grade="4",
                    password1=self.password, password2=self.password, confirm="on")
        data.update(changes)
        return data

    def login(self, client=None, user=None):
        client = client or self.client
        user = user or self.teacher
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def test_account_profile_enrollment_and_hash(self):
        student = self.create()
        self.assertEqual(student.organization_id, self.org.pk)
        self.assertEqual(student.role, "STUDENT")
        self.assertFalse(student.is_staff)
        self.assertFalse(student.is_superuser)
        self.assertEqual(student.email, "")
        self.assertTrue(student.check_password(self.password))
        self.assertNotEqual(student.password, self.password)
        self.assertEqual(student.student_profile.grade, "4")
        self.assertTrue(ClassEnrollment.objects.get(classroom=self.room, student=student).is_active)
        self.assertIsNone(StaffEmailBackend().get_user(student.pk))

    def test_initial_shared_access_is_class_scoped(self):
        student = self.create()
        for instructor in (self.teacher, self.shared):
            self.assertTrue(visible_students(instructor).filter(pk=student.pk).exists())
        self.assertFalse(visible_students(self.unassigned).filter(pk=student.pk).exists())
        ClassEnrollment.objects.filter(classroom=self.room, student=student).update(is_active=False)
        self.assertFalse(visible_students(self.teacher).filter(pk=student.pk).exists())

    def test_owner_can_create_without_instructor_membership(self):
        student = self.create(self.owner, classroom_id=self.extra.pk)
        self.assertTrue(ClassEnrollment.objects.filter(classroom=self.extra, student=student).exists())

    def test_unassigned_and_removed_membership_denied(self):
        for actor in (self.unassigned, self.teacher):
            if actor == self.teacher:
                ClassInstructor.objects.filter(classroom=self.room, instructor=actor).update(is_active=False)
            with self.subTest(actor=actor.pk), self.assertRaises(PermissionDenied):
                self.create(actor)
        self.assertFalse(get_user_model().objects.filter(username="learner").exists())

    def test_cross_org_and_archived_class_denied(self):
        foreign = Classroom.objects.create(organization=self.other, name="Foreign", created_by=self.owner)
        with self.assertRaises(PermissionDenied):
            self.create(classroom_id=foreign.pk)
        Classroom.objects.filter(pk=self.room.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.create()

    def test_invalid_grade_weak_password_and_username_leave_no_partial_account(self):
        for change in ({"grade": "9"}, {"password": "123"}, {"username": "bad name"}):
            with self.subTest(change=change), self.assertRaises(ValidationError):
                self.create(**change)
        self.assertFalse(get_user_model().objects.filter(role="STUDENT").exists())
        self.assertFalse(StudentProfile.objects.exists())
        self.assertFalse(ClassEnrollment.objects.exists())

    def test_global_username_conflict_is_generic_and_atomic(self):
        get_user_model().objects.create_user(username="learner", organization=self.other, role="STUDENT")
        with self.assertRaisesMessage(ValidationError, "Unable to create student"):
            self.create()
        self.assertEqual(get_user_model().objects.filter(username="learner").count(), 1)
        self.assertFalse(StudentProfile.objects.exists())
        self.assertFalse(ClassEnrollment.objects.exists())

    def test_profile_failure_rolls_back_account(self):
        with patch("apps.classrooms.student_services.StudentProfile.save", side_effect=RuntimeError("synthetic")):
            with self.assertRaises(RuntimeError):
                self.create()
        self.assertFalse(get_user_model().objects.filter(username="learner").exists())

    def test_enrollment_failure_rolls_back_account_and_profile(self):
        with patch("apps.classrooms.student_services.ClassEnrollment.save", side_effect=IntegrityError("synthetic")):
            with self.assertRaises(ValidationError):
                self.create()
        self.assertFalse(get_user_model().objects.filter(username="learner").exists())
        self.assertFalse(StudentProfile.objects.exists())

    def test_current_actor_and_mfa_rechecked(self):
        get_user_model().objects.filter(pk=self.teacher.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.create()
        self.owner.is_verified = lambda: False
        with self.assertRaises(PermissionDenied):
            self.create(self.owner)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_disabled_feature_denies_service_and_route(self):
        with self.assertRaises(PermissionDenied):
            self.create()
        self.login()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_form_get_is_read_only_private_and_password_fields_hidden(self):
        self.login()
        response = self.client.get(self.url)
        self.assertContains(response, 'type="password"', count=2)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertFalse(StudentProfile.objects.exists())

    def test_ui_creation_ignores_privilege_injection_and_preserves_staff_session(self):
        self.login()
        response = self.client.post(self.url, self.payload(
            role="OWNER", organization=str(self.other.pk), is_staff="true", is_superuser="true",
        ))
        self.assertRedirects(response, reverse("classrooms:detail", args=[self.room.pk]),
                             fetch_redirect_response=False)
        student = get_user_model().objects.get(username="learner")
        self.assertEqual(student.role, "STUDENT")
        self.assertEqual(student.organization_id, self.org.pk)
        self.assertFalse(student.is_superuser)
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.teacher.pk))
        self.assertNotIn(self.password, response.content.decode())

    def test_confirmation_mismatch_and_invalid_grade_do_not_create(self):
        self.login()
        for changes in ({"confirm": ""}, {"password2": "different"}, {"grade": "9"}):
            response = self.client.post(self.url, self.payload(**changes))
            self.assertEqual(response.status_code, 400)
            self.assertNotContains(response, self.password, status_code=400)
        self.assertFalse(StudentProfile.objects.exists())

    def test_inaccessible_class_hidden_and_unverified_redirected(self):
        self.login(user=self.unassigned)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.post(self.url, self.payload()).status_code, 404)
        client = Client()
        client.force_login(self.owner)
        self.assertEqual(client.get(self.url).status_code, 302)
        self.assertEqual(Client().get(self.url).status_code, 302)

    def test_csrf_missing_null_cross_and_same_origin(self):
        client = Client(enforce_csrf_checks=True)
        self.login(client)
        self.assertEqual(client.post(self.url, self.payload()).status_code, 403)
        self.assertEqual(client.get(self.url).status_code, 200)
        data = self.payload(csrfmiddlewaretoken=client.cookies["csrftoken"].value)
        for origin in ("null", "https://attacker.example"):
            self.assertEqual(client.post(self.url, data, HTTP_ORIGIN=origin).status_code, 403)
        self.assertFalse(StudentProfile.objects.exists())
        self.assertEqual(client.post(self.url, data, HTTP_ORIGIN="http://testserver").status_code, 302)
