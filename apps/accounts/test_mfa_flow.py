from base64 import b32decode

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY, verify_token
from django_otp.oath import totp
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class StaffMFAFlowTests(TestCase):
    password = "Synthetic-MFA-Password!97531"

    @classmethod
    def setUpTestData(cls):
        organization = Organization.objects.create(name="Synthetic Center")
        cls.owner = get_user_model().objects.create_user(
            username="owner", email="owner@example.test", password=cls.password,
            role="OWNER", organization=organization,
        )
        cls.student = get_user_model().objects.create_user(
            username="student", email="student@example.test", password=cls.password,
            role="STUDENT", organization=organization,
        )

    def auth_step(self):
        url = reverse("two_factor:login")
        page = self.client.get(url)
        prefix = page.context["wizard"]["management_form"].prefix
        return self.client.post(url, {
            f"{prefix}-current_step": "auth",
            "auth-username": self.owner.email,
            "auth-password": self.password,
        })

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_feature_disabled_by_default_gate(self):
        self.assertEqual(self.client.get(reverse("two_factor:login")).status_code, 404)

    def test_login_displays_email_field(self):
        page = self.client.get(reverse("two_factor:login"))
        self.assertContains(page, "Email")
        self.assertNotContains(page, "cdnjs.cloudflare.com")

    def test_anonymous_cannot_open_staff_workspace(self):
        self.assertRedirects(self.client.get(reverse("staff-home")),
                             reverse("two_factor:login"), fetch_redirect_response=False)

    def test_first_factor_without_device_redirects_to_enrollment(self):
        response = self.auth_step()
        self.assertRedirects(response, reverse("two_factor:setup"),
                             fetch_redirect_response=False)
        self.assertRedirects(self.client.get(reverse("staff-home")),
                             reverse("two_factor:login"), fetch_redirect_response=False)

    def test_enrollment_wizard_confirms_real_totp(self):
        self.client.force_login(self.owner)
        url = reverse("two_factor:setup")
        first = self.client.get(url)
        prefix = first.context["wizard"]["management_form"].prefix
        generator = self.client.post(url, {f"{prefix}-current_step": "welcome"})
        secret = generator.context["secret_key"]
        key = b32decode(secret + "=" * (-len(secret) % 8))
        token = str(totp(key)).zfill(6)
        response = self.client.post(url, {
            f"{prefix}-current_step": "generator", "generator-token": token,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TOTPDevice.objects.filter(user=self.owner, confirmed=True).exists())
        self.assertEqual(self.client.get(reverse("staff-home")).status_code, 200)

    def test_password_plus_real_totp_opens_workspace(self):
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        page = self.auth_step()
        self.assertEqual(page.context["wizard"]["steps"].current, "token")
        prefix = page.context["wizard"]["management_form"].prefix
        token = str(totp(device.bin_key)).zfill(6)
        response = self.client.post(reverse("two_factor:login"), {
            f"{prefix}-current_step": "token", "token-otp_token": token,
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(DEVICE_ID_SESSION_KEY, self.client.session)
        self.assertEqual(self.client.get(reverse("staff-home")).status_code, 200)

    def test_invalid_totp_does_not_authenticate(self):
        TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        page = self.auth_step()
        prefix = page.context["wizard"]["management_form"].prefix
        response = self.client.post(reverse("two_factor:login"), {
            f"{prefix}-current_step": "token", "token-otp_token": "invalid",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(DEVICE_ID_SESSION_KEY, self.client.session)

    def test_real_totp_cannot_be_replayed(self):
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        token = str(totp(device.bin_key)).zfill(6)
        self.assertIsNotNone(verify_token(self.owner, device.persistent_id, token))
        self.assertIsNone(verify_token(self.owner, device.persistent_id, token))

    def test_static_recovery_token_is_one_time(self):
        device = StaticDevice.objects.create(user=self.owner, name="backup", confirmed=True)
        token = StaticToken.random_token()
        StaticToken.objects.create(device=device, token=token)
        self.assertIsNotNone(verify_token(self.owner, device.persistent_id, token))
        self.assertIsNone(verify_token(self.owner, device.persistent_id, token))

    def test_unverified_session_cannot_read_recovery_codes(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("two_factor:backup_tokens"))
        self.assertRedirects(response, reverse("two_factor:login"),
                             fetch_redirect_response=False)

    def test_student_cannot_authenticate_through_staff_backend(self):
        self.assertFalse(self.client.login(username=self.student.email, password=self.password))

    def test_post_logout_invalidates_session(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("staff-logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_rejects_get(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("staff-logout")).status_code, 405)

    def test_login_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse("two_factor:login"), {}).status_code, 403)

    def test_verified_staff_cannot_disable_mfa(self):
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        self.client.force_login(self.owner)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        response = self.client.post(reverse("two_factor:disable"), {"understand": "on"})
        self.assertEqual(response.status_code, 403)
        self.assertTrue(TOTPDevice.objects.filter(pk=device.pk).exists())
