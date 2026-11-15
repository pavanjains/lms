from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from apps.accounts.backends import StaffEmailBackend
from apps.accounts.policies import staff_mfa_required
from apps.organizations.models import Organization


@override_settings(AUTHENTICATION_BACKENDS=["apps.accounts.backends.StaffEmailBackend"])
class StaffAccessTests(TestCase):
    password = "Synthetic-Staff-Password!84723"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.organization = Organization.objects.create(name="Synthetic Center")
        cls.owner = User.objects.create_user(
            username="owner", email="owner@example.test", password=cls.password,
            organization=cls.organization, role=User.Role.OWNER,
        )
        cls.instructor = User.objects.create_user(
            username="teacher", email="teacher@example.test", password=cls.password,
            organization=cls.organization, role=User.Role.INSTRUCTOR,
        )
        cls.student = User.objects.create_user(
            username="student", email="student@example.test", password=cls.password,
            organization=cls.organization, role=User.Role.STUDENT,
        )

    def protected_request(self, user):
        request = RequestFactory().get("/staff/example/")
        request.user = user
        view = staff_mfa_required(lambda request: HttpResponse("protected"))
        return view(request)

    def test_owner_authenticates_by_normalized_email(self):
        user = authenticate(username=" OWNER@EXAMPLE.TEST ", password=self.password)
        self.assertEqual(user.pk, self.owner.pk)

    def test_instructor_authenticates_by_email_keyword(self):
        user = authenticate(email="teacher@example.test", password=self.password)
        self.assertEqual(user.pk, self.instructor.pk)

    def test_username_is_not_staff_login_identifier(self):
        self.assertIsNone(authenticate(username="teacher", password=self.password))

    def test_wrong_password_is_rejected(self):
        self.assertIsNone(authenticate(username=self.owner.email, password="incorrect"))

    def test_missing_credentials_are_rejected(self):
        self.assertIsNone(authenticate(username=self.owner.email))
        self.assertIsNone(authenticate(password=self.password))

    def test_student_is_rejected_even_with_valid_password(self):
        self.assertIsNone(authenticate(username=self.student.email, password=self.password))

    def test_inactive_staff_is_rejected(self):
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        self.assertIsNone(authenticate(username=self.owner.email, password=self.password))
        self.assertIsNone(StaffEmailBackend().get_user(self.owner.pk))

    def test_inactive_organization_is_rejected(self):
        self.organization.is_active = False
        self.organization.save(update_fields=["is_active"])
        self.assertIsNone(authenticate(username=self.owner.email, password=self.password))
        self.assertIsNone(StaffEmailBackend().get_user(self.owner.pk))

    def test_unknown_email_is_rejected(self):
        self.assertIsNone(authenticate(username="missing@example.test", password=self.password))

    def test_session_lookup_rejects_missing_and_student_users(self):
        self.assertIsNone(StaffEmailBackend().get_user(self.owner.pk + 10000))
        self.assertIsNone(StaffEmailBackend().get_user(self.student.pk))

    def test_anonymous_request_is_denied(self):
        with self.assertRaises(PermissionDenied):
            self.protected_request(AnonymousUser())

    def test_password_only_staff_session_is_denied(self):
        with self.assertRaises(PermissionDenied):
            self.protected_request(self.owner)

    def test_unverified_staff_session_is_denied(self):
        with patch.object(self.owner, "is_verified", return_value=False, create=True):
            with self.assertRaises(PermissionDenied):
                self.protected_request(self.owner)

    def test_verified_staff_session_is_allowed_and_not_cached(self):
        with patch.object(self.owner, "is_verified", return_value=True, create=True):
            response = self.protected_request(self.owner)
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])

    def test_verification_does_not_override_student_role(self):
        with patch.object(self.student, "is_verified", return_value=True, create=True):
            with self.assertRaises(PermissionDenied):
                self.protected_request(self.student)

    def test_verification_does_not_override_disabled_organization(self):
        self.organization.is_active = False
        self.organization.save(update_fields=["is_active"])
        owner = get_user_model().objects.select_related("organization").get(pk=self.owner.pk)
        with patch.object(owner, "is_verified", return_value=True, create=True):
            with self.assertRaises(PermissionDenied):
                self.protected_request(owner)
