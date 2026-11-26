from django.contrib.auth import SESSION_KEY, get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts import throttle
from apps.accounts.models import StudentProfile
from apps.classrooms.credential_services import reset_student_credentials
from apps.classrooms.models import ClassEnrollment, Classroom
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class CredentialResetClearsLockoutTests(TestCase):
    old = "Synthetic-Previous-Password!4321"

    def setUp(self):
        org = Organization.objects.create(name="Synthetic center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", role="OWNER",
            organization=org, password=self.old,
        )
        self.owner.is_verified = lambda: True
        self.outsider = User.objects.create_user(
            username="outsider", email="outsider@example.test", role="INSTRUCTOR",
            organization=org, password=self.old,
        )
        self.outsider.is_verified = lambda: True
        self.student = User.objects.create_user(
            username="learner", email="", role="STUDENT", organization=org, password=self.old,
        )
        StudentProfile.objects.create(user=self.student, grade="4")
        self.room = Classroom.objects.create(organization=org, name="Robotics", created_by=self.owner)
        ClassEnrollment.objects.create(classroom=self.room, student=self.student)

    def lock(self, name):
        for _ in range(throttle.MAX_FAILURES):
            throttle.record_failure(throttle.STUDENT, name)
        self.assertTrue(throttle.is_locked(throttle.STUDENT, name))

    def reset(self, actor=None):
        return reset_student_credentials(
            actor=actor or self.owner, classroom_id=self.room.pk, student_id=self.student.pk,
        )

    def test_reset_clears_the_lock_and_the_new_password_signs_in(self):
        self.lock("learner")
        credentials = self.reset()
        self.assertFalse(throttle.is_locked(throttle.STUDENT, "learner"))
        response = self.client.post(reverse("student-login"), {
            "student_username": credentials.username, "password": credentials.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(str(self.client.session[SESSION_KEY]), str(self.student.pk))

    def test_lock_under_a_different_spelling_of_the_name_is_also_cleared(self):
        self.lock("  LEARNER ")
        self.reset()
        self.assertFalse(throttle.is_locked(throttle.STUDENT, "learner"))

    def test_other_names_stay_locked(self):
        self.lock("someone-else")
        self.lock("learner")
        self.reset()
        self.assertTrue(throttle.is_locked(throttle.STUDENT, "someone-else"))

    def test_denied_reset_leaves_the_lock_in_place(self):
        self.lock("learner")
        with self.assertRaises(PermissionDenied):
            self.reset(self.outsider)
        self.assertTrue(throttle.is_locked(throttle.STUDENT, "learner"))
