from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts import mfa_policy
from apps.accounts.mfa_policy_models import InstallationMfaPolicy, InstallationMfaPolicyAudit
from apps.accounts.mfa_policy_views import REVIEW_KEY, REVIEW_SALT
from apps.organizations.models import Organization


@override_settings(
    DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_DEPLOYMENT_MODE="local",
    LMS_LOCAL_MFA_POLICY_ENABLED=True, LMS_INSTALLATION_ADMIN_USERNAME="owner",
)
class MfaPolicyControlsTests(TestCase):
    password = "Synthetic-Mfa-Controls-Only!298471"

    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic MFA center")
        self.owner = get_user_model().objects.create_user(
            username="owner", email="owner@example.test", password=self.password,
            role="OWNER", organization=self.org,
        )
        self.owner.is_verified = lambda: True
        self.login(self.client, self.owner)
        self.url = reverse("owner-accounts:mfa-policy")

    def login(self, client, user):
        device, _ = TOTPDevice.objects.get_or_create(user=user, name="default", defaults={"confirmed": True})
        client.force_login(user, backend="apps.accounts.backends.StaffEmailBackend")
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def review(self, client=None):
        response = (client or self.client).post(self.url, {"action": "review", "expected_version": 1})
        self.assertEqual(response.status_code, 200)
        return response.context["mfa_confirm_form"].initial["token"]

    def confirm(self, token, client=None, **changes):
        return (client or self.client).post(self.url, {
            "action": "confirm", "token": token, "password": self.password, "confirm": "on", **changes,
        })

    def change(self, required, version):
        return mfa_policy.change_policy(actor=self.owner, require_mfa=required,
                                       expected_version=version, password=self.password, confirmed=True)

    def assert_required_unchanged(self):
        policy = InstallationMfaPolicy.objects.get(pk=1)
        self.assertTrue(policy.require_mfa)
        self.assertEqual(policy.version, 1)
        self.assertFalse(InstallationMfaPolicyAudit.objects.exists())

    def test_owner_page_and_settings_have_global_checkbox(self):
        response = self.client.get(reverse("owner-accounts:instructors"))
        self.assertContains(response, 'name="require_mfa"')
        self.assertContains(response, "every organization")
        self.assertContains(response, "production always requires MFA")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["mfa_selection_form"].initial["require_mfa"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertIn("no-store", response["Cache-Control"])
        self.assert_required_unchanged()

    def test_review_alone_does_not_save_or_put_password_in_token(self):
        token = self.review()
        data = signing.loads(token, salt=REVIEW_SALT)
        self.assertEqual(data["scope"], "installation")
        self.assertFalse(data["require_mfa"])
        self.assertNotIn("password", data)
        self.assert_required_unchanged()

    def test_checkbox_required_at_confirmation(self):
        token = self.review()
        self.assertEqual(self.confirm(token, confirm="").status_code, 400)
        self.assert_required_unchanged()

    def test_confirm_saves_signed_choice_and_audit_not_posted_replacement(self):
        token = self.review()
        response = self.confirm(token, require_mfa="on", expected_version=999)
        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        policy = InstallationMfaPolicy.objects.get(pk=1)
        self.assertFalse(policy.require_mfa)
        self.assertEqual(policy.version, 2)
        event = InstallationMfaPolicyAudit.objects.get()
        self.assertTrue(event.previous_required)
        self.assertFalse(event.new_required)
        self.assertEqual(event.changed_by_id, self.owner.pk)
        self.assertEqual(event.actor_username, self.owner.username)
        self.assertNotIn(REVIEW_KEY, self.client.session)
        self.assertTrue(TOTPDevice.objects.filter(user=self.owner).exists())
        self.assertEqual(self.confirm(token).status_code, 400)
        self.assertEqual(InstallationMfaPolicyAudit.objects.count(), 1)

    def test_wrong_password_is_not_echoed_and_does_not_save(self):
        token = self.review()
        marker = "WrongPasswordMarker!892"
        response = self.confirm(token, password=marker)
        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, marker, status_code=400)
        self.assert_required_unchanged()

    def test_stale_review_does_not_overwrite_newer_policy(self):
        token = self.review()
        self.change(False, 1)
        self.change(True, 2)
        self.assertEqual(self.confirm(token).status_code, 400)
        policy = InstallationMfaPolicy.objects.get(pk=1)
        self.assertTrue(policy.require_mfa)
        self.assertEqual(policy.version, 3)
        self.assertEqual(InstallationMfaPolicyAudit.objects.count(), 2)

    def test_other_session_cannot_confirm_review(self):
        token = self.review()
        client = Client()
        self.login(client, self.owner)
        self.assertEqual(self.confirm(token, client=client).status_code, 400)
        self.assert_required_unchanged()

    def test_expired_and_tampered_tokens_are_rejected(self):
        token = self.review()
        self.assertEqual(self.confirm(token + "x").status_code, 400)
        token = self.review()
        with patch("apps.accounts.mfa_policy_views.REVIEW_SECONDS", -1):
            self.assertEqual(self.confirm(token).status_code, 400)
        self.assert_required_unchanged()

    def test_cancel_invalidates_review_without_saving(self):
        token = self.review()
        response = self.client.post(self.url, {"action": "cancel"})
        self.assertRedirects(response, reverse("owner-accounts:instructors"), fetch_redirect_response=False)
        self.assertEqual(self.confirm(token).status_code, 400)
        self.assert_required_unchanged()

    def test_other_organization_owner_has_no_global_control(self):
        other_org = Organization.objects.create(name="Other synthetic center")
        other = get_user_model().objects.create_user(
            username="otherowner", email="otherowner@example.test", role="OWNER", organization=other_org,
        )
        client = Client()
        self.login(client, other)
        self.assertNotContains(client.get(reverse("owner-accounts:instructors")), 'name="require_mfa"')
        self.assertEqual(client.get(self.url).status_code, 403)
        self.assertEqual(client.post(self.url, {"action": "review", "expected_version": 1}).status_code, 403)
        self.assert_required_unchanged()

    def test_other_roles_cannot_change_policy_through_service(self):
        for role in ("INSTRUCTOR", "STUDENT"):
            user = get_user_model().objects.create_user(
                username=role.lower(), email=role.lower() + "@example.test", role=role, organization=self.org,
            )
            user.is_verified = lambda: True
            with self.subTest(role=role), self.assertRaises(PermissionDenied):
                mfa_policy.change_policy(actor=user, require_mfa=False, expected_version=1,
                                         password=self.password, confirmed=True)
        self.assert_required_unchanged()

    def test_production_or_disabled_controls_cannot_relax_mfa(self):
        InstallationMfaPolicy.objects.filter(pk=1).update(require_mfa=False)
        for changes in ({"LMS_DEPLOYMENT_MODE": "production"}, {"LMS_LOCAL_MFA_POLICY_ENABLED": False}):
            with self.settings(**changes):
                self.assertTrue(mfa_policy.effective_mfa_required())
                self.assertEqual(self.client.get(self.url).status_code, 404)
                with self.assertRaises(PermissionDenied):
                    self.change(True, 1)
        self.assertFalse(InstallationMfaPolicyAudit.objects.exists())

    def test_password_only_can_restore_policy_but_cannot_disable_required_policy(self):
        self.change(False, 1)
        self.owner.is_verified = lambda: False
        self.change(True, 2)
        with self.assertRaises(PermissionDenied):
            self.change(False, 3)
        self.assertTrue(InstallationMfaPolicy.objects.get(pk=1).require_mfa)
        self.assertEqual(InstallationMfaPolicyAudit.objects.count(), 2)

    def test_audit_failure_rolls_back_policy_change(self):
        with patch.object(InstallationMfaPolicyAudit, "save", side_effect=RuntimeError("Synthetic audit failure")):
            with self.assertRaises(RuntimeError):
                self.change(False, 1)
        self.assert_required_unchanged()

    def test_missing_policy_is_unavailable_not_silently_created(self):
        InstallationMfaPolicy.objects.filter(pk=1).delete()
        self.assertEqual(self.client.get(self.url).status_code, 503)
        self.assertFalse(InstallationMfaPolicy.objects.exists())
        self.assertTrue(mfa_policy.effective_mfa_required())

    def test_csrf_and_method_guards_remain(self):
        client = Client(enforce_csrf_checks=True)
        self.login(client, self.owner)
        self.assertEqual(client.post(self.url, {"action": "review", "expected_version": 1}).status_code, 403)
        self.assertEqual(self.client.put(self.url).status_code, 405)
        self.assert_required_unchanged()

    def test_actor_deactivation_or_designation_change_revokes_control(self):
        with self.settings(LMS_INSTALLATION_ADMIN_USERNAME="another-owner"):
            with self.assertRaises(PermissionDenied):
                self.change(False, 1)
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.change(False, 1)
        self.assert_required_unchanged()

    def test_review_requires_an_actual_change_and_current_version(self):
        for data in ({"action": "review", "expected_version": 1, "require_mfa": "on"},
                     {"action": "review", "expected_version": 99}):
            self.assertEqual(self.client.post(self.url, data).status_code, 400)
        self.assert_required_unchanged()
