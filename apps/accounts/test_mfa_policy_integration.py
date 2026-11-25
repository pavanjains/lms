from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.mfa_policy_models import InstallationMfaPolicy
from apps.organizations.models import Organization

STAFF_BACKEND = "apps.accounts.backends.StaffEmailBackend"


@override_settings(
    DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_DEPLOYMENT_MODE="local",
    LMS_LOCAL_MFA_POLICY_ENABLED=True, LMS_INSTALLATION_ADMIN_USERNAME="owner",
)
class MfaPolicyEnforcementTests(TestCase):
    password = "Synthetic-Mfa-Integration!482913"

    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic integration center")
        self.other_org = Organization.objects.create(name="Second synthetic center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", password=self.password,
            role="OWNER", organization=self.org,
        )
        self.instructor = User.objects.create_user(
            username="teacher", email="teacher@example.test", password=self.password,
            role="INSTRUCTOR", organization=self.other_org,
        )
        self.student = User.objects.create_user(
            username="student", email="student@example.test", password=self.password,
            role="STUDENT", organization=self.org,
        )
        self.home = reverse("staff-home")
        self.login_url = reverse("two_factor:login")

    def set_required(self, required):
        InstallationMfaPolicy.objects.filter(pk=1).update(require_mfa=required)

    def password_only(self, user):
        self.client.force_login(user, backend=STAFF_BACKEND)

    def verified(self, user):
        device, _ = TOTPDevice.objects.get_or_create(user=user, name="default", defaults={"confirmed": True})
        self.client.force_login(user, backend=STAFF_BACKEND)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        return device

    def first_factor(self, user):
        page = self.client.get(self.login_url)
        prefix = page.context["wizard"]["management_form"].prefix
        return self.client.post(self.login_url, {
            f"{prefix}-current_step": "auth", "auth-username": user.email, "auth-password": self.password,
        })

    def test_default_policy_requires_mfa_for_password_only_session(self):
        self.password_only(self.owner)
        self.assertRedirects(self.client.get(self.home), self.login_url, fetch_redirect_response=False)

    def test_policy_off_allows_password_only_staff_in_every_organization(self):
        self.set_required(False)
        for user in (self.owner, self.instructor):
            with self.subTest(user=user.username):
                self.password_only(user)
                self.assertEqual(self.client.get(self.home).status_code, 200)
        self.password_only(self.owner)
        self.assertEqual(self.client.get(reverse("owner-accounts:instructors")).status_code, 200)

    def test_policy_off_never_grants_student_or_anonymous_staff_access(self):
        self.set_required(False)
        self.assertRedirects(self.client.get(self.home), self.login_url, fetch_redirect_response=False)
        self.client.force_login(self.student)
        self.assertNotEqual(self.client.get(self.home).status_code, 200)

    def test_reenabling_requires_password_only_sessions_to_verify_again(self):
        self.set_required(False)
        self.password_only(self.owner)
        self.assertEqual(self.client.get(self.home).status_code, 200)
        self.set_required(True)
        self.assertRedirects(self.client.get(self.home), self.login_url, fetch_redirect_response=False)

    def test_existing_authenticator_is_kept_and_still_works_after_off_and_on(self):
        device = self.verified(self.owner)
        self.set_required(False)
        self.set_required(True)
        self.assertTrue(TOTPDevice.objects.filter(pk=device.pk, confirmed=True).exists())
        self.assertEqual(self.client.get(self.home).status_code, 200)
        self.password_only(self.owner)
        self.assertRedirects(self.client.get(self.home), self.login_url, fetch_redirect_response=False)

    def test_login_skips_token_step_only_when_policy_is_off(self):
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        page = self.first_factor(self.owner)
        self.assertEqual(page.context["wizard"]["steps"].current, "token")
        self.client.logout()
        self.set_required(False)
        response = self.first_factor(self.owner)
        self.assertRedirects(response, reverse("staff-entry"), fetch_redirect_response=False)
        self.assertEqual(self.client.get(self.home).status_code, 200)
        self.assertTrue(TOTPDevice.objects.filter(pk=device.pk).exists())
        self.set_required(True)
        self.assertRedirects(self.client.get(self.home), self.login_url, fetch_redirect_response=False)

    def test_login_with_real_totp_still_works_when_policy_requires_mfa(self):
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        page = self.first_factor(self.owner)
        prefix = page.context["wizard"]["management_form"].prefix
        response = self.client.post(self.login_url, {
            f"{prefix}-current_step": "token", "token-otp_token": str(totp(device.bin_key)).zfill(6),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get(self.home).status_code, 200)

    def test_stored_off_is_ignored_in_production_or_when_flag_is_off(self):
        self.set_required(False)
        self.password_only(self.owner)
        for changes in ({"LMS_DEPLOYMENT_MODE": "production"}, {"LMS_LOCAL_MFA_POLICY_ENABLED": False}):
            with self.subTest(changes=changes), self.settings(**changes):
                self.assertRedirects(self.client.get(self.home), self.login_url, fetch_redirect_response=False)

    def test_inactive_staff_gets_no_relaxed_access(self):
        self.set_required(False)
        self.password_only(self.instructor)
        get_user_model().objects.filter(pk=self.instructor.pk).update(is_active=False)
        self.assertNotEqual(self.client.get(self.home).status_code, 200)
