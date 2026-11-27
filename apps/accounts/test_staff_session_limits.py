import time

from django.contrib.auth import SESSION_KEY, get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.accounts.middleware import (
    EXPIRED, START, STAFF_BACKEND, STAFF_SEEN, STAFF_STARTED, VALID, clock_state, staff_limits,
)
from apps.organizations.models import Organization

IDLE, ABSOLUTE = 1800, 28800


class ClockStateTests(SimpleTestCase):
    now = 1_000_000.0

    def state(self, started, seen):
        return clock_state(started, seen, self.now, IDLE, ABSOLUTE)

    def test_session_without_a_clock_starts_one(self):
        self.assertEqual(self.state(None, None), START)

    def test_recent_activity_is_valid(self):
        self.assertEqual(self.state(self.now - 600, self.now - 60), VALID)

    def test_idle_limit_boundary(self):
        started = self.now - 3000
        self.assertEqual(self.state(started, self.now - IDLE + 1), VALID)
        self.assertEqual(self.state(started, self.now - IDLE), EXPIRED)

    def test_absolute_limit_boundary(self):
        seen = self.now - 1
        self.assertEqual(self.state(self.now - ABSOLUTE + 1, seen), VALID)
        self.assertEqual(self.state(self.now - ABSOLUTE, seen), EXPIRED)

    def test_missing_or_malformed_timestamps_expire(self):
        good = self.now - 60
        for label, started, seen in (
            ("only started", good, None), ("only seen", None, good),
            ("text seen", good, "forged"), ("text started", "forged", good),
            ("boolean", True, good), ("nan", good, float("nan")),
            ("infinite", good, float("inf")), ("list", good, [1]),
        ):
            with self.subTest(label):
                self.assertEqual(self.state(started, seen), EXPIRED)

    def test_out_of_order_and_future_timestamps_expire(self):
        self.assertEqual(self.state(self.now - 10, self.now - 100), EXPIRED)
        self.assertEqual(self.state(self.now - 100, self.now + 60), EXPIRED)

    def test_small_clock_skew_is_tolerated(self):
        self.assertEqual(self.state(self.now - 100, self.now + 3), VALID)


class StaffLimitsTests(SimpleTestCase):
    def test_valid_limits_are_returned(self):
        with override_settings(LMS_STAFF_IDLE_SECONDS=600, LMS_STAFF_ABSOLUTE_SECONDS=3600):
            self.assertEqual(staff_limits(), (600, 3600))

    def test_invalid_limits_are_refused(self):
        for idle, absolute in ((0, 100), (200, 100), (100, 86401), (-5, 100)):
            with self.subTest(idle=idle, absolute=absolute):
                with override_settings(
                    LMS_STAFF_IDLE_SECONDS=idle, LMS_STAFF_ABSOLUTE_SECONDS=absolute,
                ):
                    with self.assertRaises(ImproperlyConfigured):
                        staff_limits()


@override_settings(
    LMS_STAFF_AUTH_ENABLED=True, LMS_STAFF_IDLE_SECONDS=IDLE, LMS_STAFF_ABSOLUTE_SECONDS=ABSOLUTE,
)
class StaffSessionMiddlewareTests(TestCase):
    password = "Synthetic-Staff-Password!84723"

    def setUp(self):
        User = get_user_model()
        self.org = Organization.objects.create(name="Synthetic center")
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", password=self.password,
            organization=self.org, role=User.Role.OWNER,
        )
        self.staff_url = reverse("staff-home")
        self.other_url = reverse("home")
        self.client.force_login(self.owner, backend=STAFF_BACKEND)

    def set_clock(self, started, seen):
        session = self.client.session
        session[STAFF_STARTED] = started
        session[STAFF_SEEN] = seen
        session.save()

    def signed_in(self):
        return SESSION_KEY in self.client.session

    def test_first_staff_request_starts_the_clock(self):
        before = time.time()
        self.client.get(self.staff_url)
        session = self.client.session
        self.assertTrue(self.signed_in())
        self.assertGreaterEqual(session[STAFF_STARTED], before)
        self.assertGreaterEqual(session[STAFF_SEEN], before)
        self.assertLessEqual(session.get_expiry_age(), IDLE)

    def test_idle_expiry_ends_the_session(self):
        now = time.time()
        self.set_clock(now - 1900, now - IDLE - 1)
        self.client.get(self.staff_url)
        self.assertFalse(self.signed_in())

    def test_absolute_expiry_ends_the_session_despite_recent_activity(self):
        now = time.time()
        self.set_clock(now - ABSOLUTE - 1, now - 1)
        self.client.get(self.staff_url)
        self.assertFalse(self.signed_in())

    def test_staff_pages_renew_idle_time_but_not_the_start(self):
        now = time.time()
        started = now - 500
        self.set_clock(started, now - 100)
        self.client.get(self.staff_url)
        session = self.client.session
        self.assertTrue(self.signed_in())
        self.assertEqual(session[STAFF_STARTED], started)
        self.assertGreaterEqual(session[STAFF_SEEN], now)

    def test_other_pages_enforce_limits_but_do_not_renew(self):
        now = time.time()
        seen = now - 100
        self.set_clock(now - 500, seen)
        self.client.get(self.other_url)
        self.assertTrue(self.signed_in())
        self.assertEqual(self.client.session[STAFF_SEEN], seen)
        self.set_clock(now - 3000, now - IDLE - 1)
        self.client.get(self.other_url)
        self.assertFalse(self.signed_in())

    def test_forged_or_partial_timestamps_end_the_session(self):
        now = time.time()
        for label, started, seen in (
            ("text seen", now - 10, "forged"), ("seen only", None, now - 10),
            ("future seen", now - 100, now + 600),
        ):
            with self.subTest(label):
                self.client.force_login(self.owner, backend=STAFF_BACKEND)
                session = self.client.session
                if started is not None:
                    session[STAFF_STARTED] = started
                session[STAFF_SEEN] = seen
                session.save()
                self.client.get(self.staff_url)
                self.assertFalse(self.signed_in())

    def test_anonymous_staff_request_creates_no_clock(self):
        self.client.logout()
        self.client.get(self.staff_url)
        self.assertNotIn(STAFF_STARTED, self.client.session)
        self.assertNotIn(STAFF_SEEN, self.client.session)
