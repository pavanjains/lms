import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPT = (
    "import importlib, json; m = importlib.import_module('config.settings.production'); "
    "print(json.dumps({'hsts': m.SECURE_HSTS_SECONDS, 'subdomains': m.SECURE_HSTS_INCLUDE_SUBDOMAINS, "
    "'preload': m.SECURE_HSTS_PRELOAD, 'proxy': m.SECURE_PROXY_SSL_HEADER, "
    "'csrf': m.CSRF_TRUSTED_ORIGINS, 'redirect': m.SECURE_SSL_REDIRECT}))"
)
DEFAULTS = {
    "hsts": 0, "subdomains": False, "preload": False, "proxy": None, "csrf": [], "redirect": True,
}


class ProductionHttpsSettingsTests(SimpleTestCase):
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

    def test_defaults_are_the_safe_choice(self):
        self.assertEqual(self.loaded(), DEFAULTS)

    def test_valid_values_are_accepted_and_normalized(self):
        values = self.loaded(
            LMS_HSTS_SECONDS=" 3600 ", LMS_HSTS_INCLUDE_SUBDOMAINS="True",
            LMS_PROXY_SSL_HEADER=" HTTP_X_FORWARDED_PROTO ",
            LMS_CSRF_TRUSTED_ORIGINS=" https://lms.example.org/ , https://b.example.org:8443 ,",
        )
        self.assertEqual(values, {
            "hsts": 3600, "subdomains": True, "preload": False,
            "proxy": ["HTTP_X_FORWARDED_PROTO", "https"],
            "csrf": ["https://lms.example.org", "https://b.example.org:8443"],
            "redirect": True,
        })

    def test_include_subdomains_is_ignored_while_hsts_is_off(self):
        self.assertEqual(self.loaded(LMS_HSTS_INCLUDE_SUBDOMAINS="true"), DEFAULTS)

    def test_longest_allowed_hsts_value_is_accepted(self):
        self.assertEqual(self.loaded(LMS_HSTS_SECONDS="31536000")["hsts"], 31536000)

    def test_invalid_hsts_seconds_are_refused(self):
        for label, value in {
            "negative": "-1", "text": "abc", "too long": "31536001", "decimal": "1.5",
            "non-ASCII digits": "\u0661\u0662",
        }.items():
            with self.subTest(label):
                self.assertRefused("LMS_HSTS_SECONDS", LMS_HSTS_SECONDS=value)

    def test_invalid_include_subdomains_value_is_refused(self):
        self.assertRefused("LMS_HSTS_INCLUDE_SUBDOMAINS", LMS_HSTS_INCLUDE_SUBDOMAINS="yes")

    def test_invalid_proxy_header_names_are_refused(self):
        for label, value in {
            "hyphenated": "X-Forwarded-Proto", "lower case": "HTTP_x_forwarded_proto",
            "prefix only": "HTTP_", "not a request header": "REMOTE_ADDR",
        }.items():
            with self.subTest(label):
                self.assertRefused("LMS_PROXY_SSL_HEADER", LMS_PROXY_SSL_HEADER=value)

    def test_invalid_csrf_origins_are_refused(self):
        for label, value in {
            "plain http": "http://lms.example.org", "with path": "https://lms.example.org/p",
            "wildcard": "https://*.example.org", "no scheme": "lms.example.org",
            "credentials": "https://user:secret@lms.example.org", "no host": "https://",
        }.items():
            with self.subTest(label):
                self.assertRefused("LMS_CSRF_TRUSTED_ORIGINS", LMS_CSRF_TRUSTED_ORIGINS=value)

    def test_one_bad_origin_in_a_list_refuses_the_whole_setting(self):
        self.assertRefused(
            "LMS_CSRF_TRUSTED_ORIGINS",
            LMS_CSRF_TRUSTED_ORIGINS="https://lms.example.org,http://other.example.org",
        )
