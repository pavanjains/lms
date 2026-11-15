from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import StudentProfile, User
from apps.organizations.models import Organization


class AccountModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(name="Test Robotics Center")

    def test_student_needs_no_email(self):
        student = User.objects.create_user(username="student01", password="test-only", organization=self.org, role=User.Role.STUDENT)
        self.assertEqual(student.email, "")
        self.assertTrue(student.check_password("test-only"))
        self.assertNotEqual(student.password, "test-only")

    def test_staff_requires_email(self):
        user = User(username="teacher", organization=self.org, role=User.Role.INSTRUCTOR)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_database_rejects_staff_without_email(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create(username="bad", organization=self.org, role=User.Role.INSTRUCTOR)

    def test_staff_email_is_case_insensitive_unique(self):
        User.objects.create_user(username="one", organization=self.org, role=User.Role.INSTRUCTOR, email="Teacher@example.test")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(username="two", organization=self.org, role=User.Role.INSTRUCTOR, email="teacher@example.test")

    def test_grade_four_has_no_automatic_kit(self):
        student = User.objects.create_user(username="grade4", organization=self.org, role=User.Role.STUDENT)
        profile = StudentProfile.objects.create(user=student, grade=StudentProfile.Grade.G4)
        self.assertEqual(profile.grade, "4")
        self.assertNotIn("kit", {field.name for field in profile._meta.fields})

    def test_staff_cannot_have_student_profile(self):
        teacher = User.objects.create_user(username="teacher", organization=self.org, role=User.Role.INSTRUCTOR, email="staff@example.test")
        profile = StudentProfile(user=teacher, grade="4")
        with self.assertRaises(ValidationError):
            profile.full_clean()
