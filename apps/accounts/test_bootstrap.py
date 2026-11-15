import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from apps.organizations.models import Organization


class BootstrapOwnerTests(TestCase):
    password = "Robotics!Only-For-Tests-83472"

    def run_bootstrap(self, **overrides):
        options = {
            "organization": "Test Robotics Center",
            "username": "center-owner",
            "email": "Owner@example.test",
            "noinput": True,
            "stdout": StringIO(),
            "stderr": StringIO(),
        }
        options.update(overrides)
        call_command("bootstrap_owner", **options)
        return options["stdout"].getvalue()

    def test_creates_owner_without_framework_superuser_privileges(self):
        with patch.dict(os.environ, {"LMS_BOOTSTRAP_PASSWORD": self.password}):
            output = self.run_bootstrap()
        owner = get_user_model().objects.get(username="center-owner")
        self.assertEqual(owner.role, "OWNER")
        self.assertEqual(owner.email, "owner@example.test")
        self.assertTrue(owner.check_password(self.password))
        self.assertFalse(owner.is_staff)
        self.assertFalse(owner.is_superuser)
        self.assertEqual(Organization.objects.count(), 1)
        self.assertNotIn(self.password, output)

    def test_repeat_does_not_reset_password_or_create_records(self):
        with patch.dict(os.environ, {"LMS_BOOTSTRAP_PASSWORD": self.password}):
            self.run_bootstrap()
        owner = get_user_model().objects.get()
        original_hash = owner.password
        with patch.dict(os.environ, {}, clear=True):
            output = self.run_bootstrap()
        owner.refresh_from_db()
        self.assertEqual(owner.password, original_hash)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(Organization.objects.count(), 1)
        self.assertIn("no changes made", output)

    def test_existing_installation_cannot_be_repurposed(self):
        organization = Organization.objects.create(name="Existing center")
        with self.assertRaises(CommandError):
            self.run_bootstrap()
        self.assertEqual(Organization.objects.get().pk, organization.pk)
        self.assertFalse(get_user_model().objects.exists())

    def test_existing_owner_is_never_promoted_or_reactivated(self):
        with patch.dict(os.environ, {"LMS_BOOTSTRAP_PASSWORD": self.password}):
            self.run_bootstrap()
        owner = get_user_model().objects.get()
        owner.is_active = False
        owner.save(update_fields=["is_active"])
        with self.assertRaises(CommandError):
            self.run_bootstrap()
        owner.refresh_from_db()
        self.assertFalse(owner.is_active)

    def test_noninteractive_requires_password(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CommandError):
                self.run_bootstrap()
        self.assertFalse(Organization.objects.exists())

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 18},
    }])
    def test_invalid_password_rolls_back_organization(self):
        with patch.dict(os.environ, {"LMS_BOOTSTRAP_PASSWORD": "short"}):
            with self.assertRaises(CommandError):
                self.run_bootstrap()
        self.assertFalse(Organization.objects.exists())
        self.assertFalse(get_user_model().objects.exists())

    def test_invalid_email_rolls_back_organization(self):
        with patch.dict(os.environ, {"LMS_BOOTSTRAP_PASSWORD": self.password}):
            with self.assertRaises(CommandError):
                self.run_bootstrap(email="invalid-email")
        self.assertFalse(Organization.objects.exists())

    def test_interactive_password_confirmation(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "apps.accounts.management.commands.bootstrap_owner.getpass.getpass",
                side_effect=[self.password, self.password],
            ):
                self.run_bootstrap(noinput=False)
        self.assertTrue(get_user_model().objects.get().check_password(self.password))

    def test_mismatched_passwords_create_nothing(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "apps.accounts.management.commands.bootstrap_owner.getpass.getpass",
                side_effect=[self.password, "different"],
            ):
                with self.assertRaises(CommandError):
                    self.run_bootstrap(noinput=False)
        self.assertFalse(Organization.objects.exists())

    def test_blank_identifiers_create_nothing(self):
        with self.assertRaises(CommandError):
            self.run_bootstrap(organization=" ")
        self.assertFalse(Organization.objects.exists())
