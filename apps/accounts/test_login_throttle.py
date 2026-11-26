from datetime import timedelta

from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts import throttle
from apps.accounts.models import LoginThrottle, StudentProfile
from apps.organizations.models import Organization

LOCKED = "Too many failed sign-in attempts"


class ThrottleServiceTests(TestCase):
    def fail(self, times, *, scope=throttle.STUDENT, name="kid", now=None):
        now = now or timezone.now()
        for _ in range(times):
            throttle.record_failure(scope, name, now=now)
        return now

    def test_locks_exactly_at_the_limit(self):
        start = self.fail(throttle.MAX_FAILURES - 1)
        self.assertFalse(throttle.is_locked(throttle.STUDENT, "kid", now=start))
        throttle.record_failure(throttle.STUDENT, "kid", now=start)
        self.assertTrue(throttle.is_locked(throttle.STUDENT, "kid", now=start))

    def test_lock_expires_after_the_lockout_period(self):
        start = self.fail(throttle.MAX_FAILURES)
        before = start + throttle.LOCKOUT - timedelta(seconds=1)
        self.assertTrue(throttle.is_locked(throttle.STUDENT, "kid", now=before))
        self.assertFalse(throttle.is_locked(throttle.STUDENT, "kid", now=start + throttle.LOCKOUT))

    def test_failure_after_expired_lock_starts_a_fresh_count(self):
        start = self.fail(throttle.MAX_FAILURES)
        later = start + throttle.LOCKOUT + timedelta(seconds=1)
        throttle.record_failure(throttle.STUDENT, "kid", now=later)
        row = LoginThrottle.objects.get()
        self.assertEqual((row.failures, row.locked_until), (1, None))

    def test_old_failures_age_out_of_the_window(self):
        start = self.fail(throttle.MAX_FAILURES - 1)
        later = start + throttle.WINDOW + timedelta(seconds=1)
        throttle.record_failure(throttle.STUDENT, "kid", now=later)
        self.assertFalse(throttle.is_locked(throttle.STUDENT, "kid", now=later))
        self.assertEqual(LoginThrottle.objects.get().failures, 1)

    def test_failures_while_locked_do_not_extend_the_lock(self):
        start = self.fail(throttle.MAX_FAILURES)
        locked_until = LoginThrottle.objects.get().locked_until
        throttle.record_failure(throttle.STUDENT, "kid", now=start + timedelta(minutes=1))
        self.assertEqual(LoginThrottle.objects.get().locked_until, locked_until)

    def test_reset_clears_the_count(self):
        self.fail(throttle.MAX_FAILURES - 1)
        throttle.reset(throttle.STUDENT, "kid")
        self.assertFalse(LoginThrottle.objects.exists())

    def test_names_and_scopes_are_independent(self):
        now = self.fail(throttle.MAX_FAILURES)
        self.assertFalse(throttle.is_locked(throttle.STUDENT, "other", now=now))
        self.assertFalse(throttle.is_locked(throttle.STAFF, "kid", now=now))

    def test_case_whitespace_and_unicode_forms_share_one_counter(self):
        now = self.fail(7, name="Kid ")
        self.fail(throttle.MAX_FAILURES - 7, name="\uff2b\uff29\uff24", now=now)
        self.assertTrue(throttle.is_locked(throttle.STUDENT, "kid", now=now))
        self.assertEqual(LoginThrottle.objects.count(), 1)

    def test_only_a_digest_of_the_name_is_stored(self):
        throttle.record_failure(throttle.STUDENT, "SecretName")
        row = LoginThrottle.objects.get()
        self.assertEqual(len(row.key_digest), 64)
        self.assertNotIn("secretname", str(row.__dict__).lower())

    def test_stale_rows_are_pruned_but_active_locks_are_kept(self):
        now = timezone.now()
        old = now - throttle.PRUNE_AFTER - timedelta(hours=1)
        LoginThrottle.objects.create(scope="student", key_digest="a" * 64, failures=3, window_started_at=old)
        LoginThrottle.objects.create(
            scope="student", key_digest="b" * 64, failures=15, window_started_at=old,
            locked_until=now + timedelta(hours=1),
        )
        throttle.record_failure(throttle.STUDENT, "someone", now=now)
        digests = set(LoginThrottle.objects.values_list("key_digest", flat=True))
        self.assertNotIn("a" * 64, digests)
        self.assertIn("b" * 64, digests)


@override_settings(LMS_STUDENT_AUTH_ENABLED=True, LMS_STAFF_AUTH_ENABLED=True)
class StudentSignInThrottleTests(TestCase):
    password = "Synthetic-Student-Password!7429"

    def setUp(self):
        org = Organization.objects.create(name="Synthetic center")
        self.users = {}
        for name in ("student-a", "student-b"):
            user = get_user_model().objects.create_user(
                username=name, email="", role="STUDENT", organization=org, password=self.password,
            )
            StudentProfile.objects.create(user=user, grade="4")
            self.users[name] = user
        self.url = reverse("student-login")

    def post(self, username, password):
        return self.client.post(self.url, {"student_username": username, "password": password})

    def test_correct_password_is_refused_once_locked(self):
        for _ in range(throttle.MAX_FAILURES):
            self.assertEqual(self.post("student-a", "wrong").status_code, 400)
        response = self.post("student-a", self.password)
        self.assertContains(response, LOCKED, status_code=429)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_other_students_are_not_affected(self):
        for _ in range(throttle.MAX_FAILURES):
            self.post("student-a", "wrong")
        self.assertEqual(self.post("student-b", self.password).status_code, 302)

    def test_unknown_names_are_throttled_with_the_same_message(self):
        for _ in range(throttle.MAX_FAILURES):
            self.assertEqual(self.post("nobody", "wrong").status_code, 400)
        self.assertContains(self.post("nobody", self.password), LOCKED, status_code=429)

    def test_success_below_the_limit_resets_the_count(self):
        for _ in range(throttle.MAX_FAILURES - 1):
            self.post("student-a", "wrong")
        self.assertEqual(self.post("student-a", self.password).status_code, 302)
        self.assertFalse(LoginThrottle.objects.exists())
        self.client.post(reverse("student-logout"))
        for _ in range(throttle.MAX_FAILURES - 1):
            self.assertEqual(self.post("student-a", "wrong").status_code, 400)
        self.assertEqual(self.post("student-a", self.password).status_code, 302)

    def test_signing_in_works_again_after_the_lock_expires(self):
        for _ in range(throttle.MAX_FAILURES):
            self.post("student-a", "wrong")
        LoginThrottle.objects.update(locked_until=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.post("student-a", self.password).status_code, 302)


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class StaffSignInThrottleTests(TestCase):
    password = "Synthetic-Staff-Password!97531"

    @classmethod
    def setUpTestData(cls):
        organization = Organization.objects.create(name="Synthetic Center")
        cls.owner = get_user_model().objects.create_user(
            username="owner", email="owner@example.test", password=cls.password,
            role="OWNER", organization=organization,
        )

    def auth(self, password, email=None):
        url = reverse("two_factor:login")
        prefix = self.client.get(url).context["wizard"]["management_form"].prefix
        return self.client.post(url, {
            f"{prefix}-current_step": "auth",
            "auth-username": email or self.owner.email, "auth-password": password,
        })

    def test_correct_password_is_refused_once_locked(self):
        for _ in range(throttle.MAX_FAILURES):
            self.assertEqual(self.auth("wrong").status_code, 200)
        response = self.auth(self.password)
        self.assertContains(response, LOCKED)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_email_case_does_not_bypass_the_limit(self):
        for _ in range(throttle.MAX_FAILURES):
            self.auth("wrong", email=self.owner.email.upper())
        self.assertContains(self.auth(self.password), LOCKED)

    def test_unknown_email_is_throttled_with_the_same_message(self):
        for _ in range(throttle.MAX_FAILURES):
            self.auth("wrong", email="nobody@example.test")
        self.assertContains(self.auth(self.password, email="nobody@example.test"), LOCKED)

    def test_success_below_the_limit_resets_the_count(self):
        for _ in range(throttle.MAX_FAILURES - 1):
            self.auth("wrong")
        self.assertEqual(self.auth(self.password).status_code, 302)
        self.assertFalse(LoginThrottle.objects.exists())
