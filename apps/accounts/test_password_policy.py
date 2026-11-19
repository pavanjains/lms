from django.conf import settings
from django.contrib.auth.password_validation import get_password_validators, validate_password
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase


class PasswordPolicyRegressionTests(SimpleTestCase):
    def validators(self):
        return get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)

    def rejection_codes(self, password):
        with self.assertRaises(ValidationError) as caught:
            validate_password(password, password_validators=self.validators())
        return {error.code for error in caught.exception.error_list}

    def test_original_four_validators_configured_in_order(self):
        names = [entry["NAME"] for entry in settings.AUTH_PASSWORD_VALIDATORS]
        self.assertEqual(names, [
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            "django.contrib.auth.password_validation.MinimumLengthValidator",
            "django.contrib.auth.password_validation.CommonPasswordValidator",
            "django.contrib.auth.password_validation.NumericPasswordValidator",
        ])

    def test_long_numeric_password_requires_numeric_rejection(self):
        self.assertIn("password_entirely_numeric", self.rejection_codes("84627519308462751930"))

    def test_minimum_length_and_common_password_checks_retained(self):
        self.assertIn("password_too_short", self.rejection_codes("Q7!"))
        self.assertIn("password_too_common", self.rejection_codes("password"))

    def test_strong_synthetic_nonnumeric_password_accepted(self):
        self.assertIsNone(validate_password(
            "Synthetic-Policy-Check!873941-Zebra", password_validators=self.validators(),
        ))
