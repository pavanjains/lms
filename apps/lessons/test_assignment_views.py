import time
from unittest.mock import patch

from django.core import signing
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.students import SEEN, STARTED, STUDENT_BACKEND
from apps.classrooms.models import ClassEnrollment, ClassInstructor
from apps.lessons import test_assignments as foundation
from apps.lessons.assignment_views import REVIEW_KEY, REVIEW_SALT
from apps.lessons.models import LessonAssignment
from apps.lessons.services import update_lesson


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class InstructorAssignmentViewsTests(TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign

    def login_staff(self, user=None, client=None):
        user, client = user or self.teacher, client or self.client
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def create_url(self):
        return reverse("lessons:assignment-create", args=[self.room.pk])

    def review(self, client=None, **changes):
        data = {"action": "review", "lesson": self.lesson.pk, "students": [self.a.pk]}
        return (client or self.client).post(self.create_url(), {**data, **changes})

    def token(self):
        response = self.review()
        self.assertEqual(response.status_code, 200)
        return response.context["form"].initial["token"]

    def confirm(self, token, **changes):
        return self.client.post(self.create_url(), {
            "action": "confirm", "token": token, "confirm": "on", **changes,
        })

    def test_get_and_review_do_not_assign_then_confirm_creates_exact_selection(self):
        self.login_staff()
        self.assertEqual(self.client.get(self.create_url()).status_code, 200)
        token = self.token()
        self.assertFalse(LessonAssignment.objects.exists())
        self.assertEqual(self.confirm(token).status_code, 302)
        self.assertEqual(LessonAssignment.objects.get().student_id, self.a.pk)
        self.assertNotIn(REVIEW_KEY, self.client.session)
        self.assertEqual(self.confirm(token).status_code, 400)
        self.assertEqual(LessonAssignment.objects.count(), 1)

    def test_direct_confirm_tampering_and_missing_checkbox_do_not_assign(self):
        self.login_staff()
        self.assertEqual(self.confirm("forged").status_code, 400)
        token = self.token()
        self.assertEqual(self.confirm(token, confirm="").status_code, 400)
        self.assertEqual(self.confirm(token + "x").status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_review_expiry_and_new_review_supersede_old_token(self):
        self.login_staff()
        first = self.token()
        second = self.token()
        self.assertNotEqual(first, second)
        self.assertEqual(self.confirm(first).status_code, 400)
        data = signing.loads(self.token(), salt=REVIEW_SALT)
        with patch.object(signing.TimestampSigner, "timestamp", return_value="0"):
            expired = signing.dumps(data, salt=REVIEW_SALT)
        session = self.client.session
        session[REVIEW_KEY] = expired
        session.save()
        self.assertEqual(self.confirm(expired).status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_review_token_cannot_be_used_in_a_different_session(self):
        self.login_staff()
        token = self.token()
        other = Client()
        self.login_staff(client=other)
        self.assertEqual(other.post(self.create_url(), {
            "action": "confirm", "token": token, "confirm": "on",
        }).status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_changed_lesson_and_revoked_enrollment_block_confirmation(self):
        self.login_staff()
        token = self.token()
        edited = update_lesson(actor=self.teacher, lesson_id=self.lesson.pk, expected_version=1,
                               **self.lesson_data(title="Changed after review"))
        self.assertEqual(self.confirm(token).status_code, 400)
        self.lesson = edited
        token = self.token()
        ClassEnrollment.objects.filter(classroom=self.room, student=self.a).update(is_active=False)
        self.assertEqual(self.confirm(token).status_code, 403)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_unassigned_instructor_and_foreign_owner_get_no_class_or_assignment(self):
        row = self.assign()[0]
        for user in (self.peer, self.foreign_owner):
            self.login_staff(user)
            self.assertEqual(self.client.get(self.create_url()).status_code, 404)
            self.assertEqual(self.client.get(reverse("lessons:assignment-detail", args=[row.pk])).status_code, 404)
            self.assertEqual(self.client.post(reverse("lessons:assignment-cancel", args=[row.pk]),
                                              {"confirm": "on", "expected_version": 1}).status_code, 404)

    def test_forged_recipients_and_duplicate_ids_rejected_at_review(self):
        self.login_staff()
        outsider = self.make_user("outside", "STUDENT", self.other_org)
        for ids in ([outsider.pk], [self.a.pk, self.a.pk], []):
            with self.subTest(ids=ids):
                self.assertEqual(self.review(students=ids).status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_removed_membership_between_review_and_confirm_is_denied(self):
        self.login_staff()
        token = self.token()
        ClassInstructor.objects.filter(classroom=self.room, instructor=self.teacher).update(is_active=False)
        self.assertEqual(self.confirm(token).status_code, 404)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_list_detail_escape_snapshots_and_apply_cache_referrer_policy(self):
        self.lesson = update_lesson(actor=self.teacher, lesson_id=self.lesson.pk, expected_version=1,
                                   **self.lesson_data(instructions="<script>bad()</script>"))
        row = self.assign()[0]
        self.login_staff()
        url = reverse("lessons:assignment-detail", args=[row.pk])
        response = self.client.get(url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertContains(self.client.get(reverse("lessons:assignment-list")), row.title)

    def test_cancel_requires_post_checkbox_and_current_version(self):
        row = self.assign()[0]
        self.login_staff()
        url = reverse("lessons:assignment-cancel", args=[row.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {"expected_version": 1}).status_code, 400)
        self.assertEqual(self.client.post(url, {"expected_version": 99, "confirm": "on"}).status_code, 400)
        row.refresh_from_db()
        self.assertIsNone(row.cancelled_at)
        self.assertEqual(self.client.post(url, {"expected_version": 1, "confirm": "on"}).status_code, 302)
        row.refresh_from_db()
        self.assertIsNotNone(row.cancelled_at)
        self.assertContains(self.client.get(reverse("lessons:assignment-detail", args=[row.pk])), "History retained")

    def test_csrf_origin_and_methods_for_selection_confirmation_and_cancellation(self):
        client = Client(enforce_csrf_checks=True)
        self.login_staff(client=client)
        url = self.create_url()
        self.assertEqual(self.review(client=client).status_code, 403)
        client.get(url)
        csrf = client.cookies["csrftoken"].value
        data = {"action": "review", "lesson": self.lesson.pk, "students": [self.a.pk],
                "csrfmiddlewaretoken": csrf}
        for origin in ("null", "https://attacker.example"):
            self.assertEqual(client.post(url, data, HTTP_ORIGIN=origin).status_code, 403)
        response = client.post(url, data, HTTP_ORIGIN="http://testserver")
        self.assertEqual(response.status_code, 200)
        token = response.context["form"].initial["token"]
        confirm = {"action": "confirm", "token": token, "confirm": "on"}
        self.assertEqual(client.post(url, confirm).status_code, 403)
        confirm["csrfmiddlewaretoken"] = csrf
        self.assertEqual(client.post(url, confirm, HTTP_ORIGIN="null").status_code, 403)
        self.assertEqual(client.post(url, confirm, HTTP_ORIGIN="http://testserver").status_code, 302)
        cancel = reverse("lessons:assignment-cancel", args=[LessonAssignment.objects.get().pk])
        self.assertEqual(client.post(cancel, {"confirm": "on", "expected_version": 1}).status_code, 403)
        self.assertEqual(client.post(cancel, {"confirm": "on", "expected_version": 1,
                                             "csrfmiddlewaretoken": csrf}, HTTP_ORIGIN="null").status_code, 403)
        self.assertEqual(client.put(url, {}, HTTP_X_CSRFTOKEN=csrf).status_code, 405)

    def test_anonymous_unverified_student_and_disabled_staff_flag_denied(self):
        url = reverse("lessons:assignment-list")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.a, backend=STUDENT_BACKEND)
        session = self.client.session
        session[STARTED] = session[SEEN] = time.time()
        session.save()
        self.assertEqual(self.client.get(url).status_code, 403)
        self.login_staff()
        with self.settings(LMS_STAFF_AUTH_ENABLED=False):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_confirmation_ignores_unreviewed_recipient_and_lesson_fields(self):
        self.login_staff()
        token = self.token()
        self.assertEqual(self.confirm(token, students=[self.b.pk], lesson=999999).status_code, 302)
        row = LessonAssignment.objects.get()
        self.assertEqual(row.student_id, self.a.pk)
        self.assertEqual(row.lesson_id, self.lesson.pk)

    def test_signed_review_is_bound_to_actor_even_if_copied_into_another_session(self):
        self.login_staff()
        token = self.token()
        self.login_staff(self.owner)
        session = self.client.session
        session[REVIEW_KEY] = token
        session.save()
        self.assertEqual(self.confirm(token).status_code, 403)
        self.assertFalse(LessonAssignment.objects.exists())
