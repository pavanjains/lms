import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPT = (
    "import importlib, json; m = importlib.import_module('config.settings.production'); "
    "print(json.dumps({'enabled': m.LMS_INSTRUCTOR_ONBOARDING_ENABLED, "
    "'origin': m.LMS_PUBLIC_ORIGIN, 'sender': m.LMS_INVITATION_FROM_EMAIL}))"
)
GOOD_ORIGIN = "https://lms.example.org"
GOOD_SENDER = "invites@example.org"


class ProductionInvitationSettingsTests(SimpleTestCase):
    def load(self, **extra):
        env = {
            key: value for key, value in os.environ.items()
            if not key.startswith(("LMS_", "DJANGO_", "POSTGRES_"))
        }
        env.update(
            DJANGO_SECRET_KEY="p" * 60, POSTGRES_PASSWORD="synthetic-test-value",
            DJANGO_ALLOWED_HOSTS="lms.example.org",
        )
        env.update(extra)
        return subprocess.run(
            [sys.executable, "-c", SCRIPT], cwd=BASE_DIR, env=env,
            capture_output=True, text=True, timeout=120,
        )

    def loaded(self, **extra):
        result = self.load(**extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout.strip().splitlines()[-1])

    def test_onboarding_is_off_by_default_with_blank_invitation_settings(self):
        values = self.loaded()
        self.assertEqual(values, {"enabled": False, "origin": "", "sender": ""})

    def test_disabled_onboarding_ignores_invitation_variables(self):
        values = self.loaded(
            LMS_PUBLIC_ORIGIN="http://bad.example.org/path", LMS_INVITATION_FROM_EMAIL="not-an-address",
        )
        self.assertEqual(values, {"enabled": False, "origin": "", "sender": ""})

    def test_valid_https_origin_and_sender_are_accepted_and_normalized(self):
        values = self.loaded(
            LMS_INSTRUCTOR_ONBOARDING_ENABLED="true",
            LMS_PUBLIC_ORIGIN=GOOD_ORIGIN + "/", LMS_INVITATION_FROM_EMAIL=GOOD_SENDER,
        )
        self.assertEqual(values, {"enabled": True, "origin": GOOD_ORIGIN, "sender": GOOD_SENDER})

    def test_enabled_onboarding_refuses_unsafe_or_missing_origin(self):
        bad_origins = {
            "missing": "",
            "plain http": "http://lms.example.org",
            "loopback http": "http://localhost:8000",
            "with path": GOOD_ORIGIN + "/invite",
            "with credentials": "https://user:secret@lms.example.org",
            "with query": GOOD_ORIGIN + "?x=1",
            "no host": "https://",
        }
        for label, origin in bad_origins.items():
            with self.subTest(label):
                result = self.load(
                    LMS_INSTRUCTOR_ONBOARDING_ENABLED="true", LMS_PUBLIC_ORIGIN=origin,
                    LMS_INVITATION_FROM_EMAIL=GOOD_SENDER,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("LMS_PUBLIC_ORIGIN", result.stderr)

    def test_enabled_onboarding_refuses_missing_or_invalid_sender(self):
        for label, sender in {"missing": "", "invalid": "not-an-address"}.items():
            with self.subTest(label):
                result = self.load(
                    LMS_INSTRUCTOR_ONBOARDING_ENABLED="true", LMS_PUBLIC_ORIGIN=GOOD_ORIGIN,
                    LMS_INVITATION_FROM_EMAIL=sender,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("LMS_INVITATION_FROM_EMAIL", result.stderr)

    def test_local_policy_controls_are_still_refused_in_production(self):
        result = self.load(LMS_DEPLOYMENT_MODE="local")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Local MFA policy controls", result.stderr)
