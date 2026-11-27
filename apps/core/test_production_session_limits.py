import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPT = (
    "import importlib, json; m = importlib.import_module('config.settings.production'); "
    "print(json.dumps({'staff': [m.LMS_STAFF_IDLE_SECONDS, m.LMS_STAFF_ABSOLUTE_SECONDS], "
    "'student': [m.LMS_STUDENT_IDLE_SECONDS, m.LMS_STUDENT_ABSOLUTE_SECONDS]}))"
)


class ProductionSessionLimitSettingsTests(SimpleTestCase):
    """Loads the production settings in a subprocess with synthetic values (same approach as
    test_production_settings.py; the helper is copied, not shared)."""

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

    def assertRefused(self, name, **extra):
        result = self.load(**extra)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(name, result.stderr)

    def test_defaults_are_the_approved_limits(self):
        self.assertEqual(self.loaded(), {"staff": [1800, 28800], "student": [3600, 14400]})

    def test_valid_overrides_are_accepted(self):
        values = self.loaded(
            LMS_STAFF_IDLE_SECONDS="600", LMS_STAFF_ABSOLUTE_SECONDS="3600",
            LMS_STUDENT_IDLE_SECONDS="1200", LMS_STUDENT_ABSOLUTE_SECONDS="7200",
        )
        self.assertEqual(values, {"staff": [600, 3600], "student": [1200, 7200]})

    def test_invalid_staff_limits_are_refused(self):
        for label, extra in {
            "idle above default absolute": {"LMS_STAFF_IDLE_SECONDS": "30000"},
            "absolute above one day": {"LMS_STAFF_ABSOLUTE_SECONDS": "86401"},
            "zero idle": {"LMS_STAFF_IDLE_SECONDS": "0"},
        }.items():
            with self.subTest(label):
                self.assertRefused("LMS_STAFF_IDLE_SECONDS", **extra)

    def test_invalid_student_limits_are_refused(self):
        for label, extra in {
            "idle above default absolute": {"LMS_STUDENT_IDLE_SECONDS": "15000"},
            "absolute above one day": {"LMS_STUDENT_ABSOLUTE_SECONDS": "86401"},
            "zero idle": {"LMS_STUDENT_IDLE_SECONDS": "0"},
        }.items():
            with self.subTest(label):
                self.assertRefused("LMS_STUDENT_IDLE_SECONDS", **extra)

    def test_non_numeric_limits_stop_startup(self):
        for name in ("LMS_STAFF_IDLE_SECONDS", "LMS_STUDENT_ABSOLUTE_SECONDS"):
            with self.subTest(name):
                self.assertNotEqual(self.load(**{name: "soon"}).returncode, 0)
