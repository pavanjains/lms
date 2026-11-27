from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event
from time import monotonic
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, connections, transaction
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, Classroom
from apps.lessons import assignments
from apps.lessons.models import LessonAssignment
from apps.lessons.services import archive_lesson, create_lesson
from apps.organizations.models import Organization

LESSON_URL = "https://education.lego.com/en-us/lessons/synthetic-not-verified/"


def synthetic_lesson(owner):
    return create_lesson(
        actor=owner, title="Synthetic race lesson", summary="Concurrency fixture",
        lego_url=LESSON_URL, instructions="Build with your instructor.",
        kit="ESSENTIAL", min_grade=4, max_grade=4,
    )


class RaceHarness:
    """Ordered two-transaction harness; same approach as ClassroomConcurrencyTests."""

    def spec(self, function, actor=None, **kwargs):
        return function, (actor or self.owner).pk, kwargs

    @staticmethod
    def worker(spec, pids, held=None, release=None):
        connections.close_all()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET lock_timeout = '15s'")
                cursor.execute("SET statement_timeout = '20s'")
                cursor.execute("SET default_transaction_isolation = 'read committed'")
                cursor.execute("SELECT pg_backend_pid()")
                pids.put(cursor.fetchone()[0])
            function, actor_id, kwargs = spec
            actor = get_user_model().objects.select_related("organization").get(pk=actor_id)
            actor.is_verified = lambda: True
            try:
                with transaction.atomic():
                    result = function(actor=actor, **kwargs)
                    if held is not None:
                        held.set()
                        if not release.wait(40):
                            raise AssertionError("Leader release timed out.")
                return "ok", getattr(result, "pk", None)
            except PermissionDenied:
                return "denied", None
            except ValidationError:
                return "invalid", None
        finally:
            connections.close_all()

    def ordered_race(self, first, second):
        held, release = Event(), Event()
        first_pids, second_pids = Queue(), Queue()
        with ThreadPoolExecutor(max_workers=2) as pool:
            leader = pool.submit(self.worker, first, first_pids, held, release)
            try:
                leader_pid = first_pids.get(timeout=10)
                if not held.wait(10):
                    leader.result(timeout=25)
                    self.fail("Leader did not reach its uncommitted write.")
                follower = pool.submit(self.worker, second, second_pids)
                follower_pid = second_pids.get(timeout=10)
                self.assertNotEqual(leader_pid, follower_pid)
                deadline = monotonic() + 8
                blocked = False
                while monotonic() < deadline:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT %s = ANY(pg_blocking_pids(%s))",
                                       [leader_pid, follower_pid])
                        blocked = cursor.fetchone()[0]
                    if blocked:
                        break
                    if follower.done():
                        follower.result()
                        self.fail("Follower completed without the expected lock wait.")
                    release.wait(0.02)
                self.assertTrue(blocked, "PostgreSQL never reported the leader blocking the follower.")
            finally:
                release.set()
            first_result = leader.result(timeout=30)
            second_result = follower.result(timeout=30)
        self.assertEqual(first_result[0], "ok")
        return first_result, second_result


@skipUnless(connection.vendor == "postgresql", "Requires real PostgreSQL row locks.")
@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class AssignmentConcurrencyTests(RaceHarness, TransactionTestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic assignment race center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="race-owner", email="race-owner@example.test",
            role="OWNER", organization=self.org,
        )
        self.owner.is_verified = lambda: True
        self.room = Classroom.objects.create(
            organization=self.org, name="Race builders", created_by=self.owner,
        )
        self.students = []
        for name in ("race-a", "race-b"):
            student = User.objects.create_user(username=name, role="STUDENT", organization=self.org)
            StudentProfile.objects.create(user=student, grade="4")
            ClassEnrollment.objects.create(classroom=self.room, student=student)
            self.students.append(student)
        self.lesson = synthetic_lesson(self.owner)

    def assign(self, students=None):
        chosen = students if students is not None else self.students
        return self.spec(
            assignments.create_assignments, classroom_id=self.room.pk,
            lesson_id=self.lesson.pk, student_ids=[student.pk for student in chosen],
            expected_lesson_version=self.lesson.version,
        )

    def cancel(self, row):
        return self.spec(assignments.cancel_assignment, assignment_id=row.pk,
                         expected_version=row.version)

    def rows(self, **filters):
        return LessonAssignment.objects.filter(classroom=self.room, lesson=self.lesson, **filters)

    def test_double_confirm_creates_one_assignment_per_student(self):
        first, second = self.ordered_race(self.assign(), self.assign())
        self.assertEqual(second[0], "invalid")
        self.assertEqual(self.rows().count(), 2)
        self.assertEqual(self.rows(cancelled_at__isnull=True).count(), 2)

    def test_overlapping_batch_creates_no_partial_rows(self):
        _, second = self.ordered_race(self.assign(self.students[:1]), self.assign())
        self.assertEqual(second[0], "invalid")
        self.assertEqual(self.rows().count(), 1)
        self.assertFalse(self.rows(student=self.students[1]).exists())

    def test_cancel_commits_before_reassignment(self):
        row = assignments.create_assignments(
            actor=self.owner, classroom_id=self.room.pk, lesson_id=self.lesson.pk,
            student_ids=[self.students[0].pk], expected_lesson_version=self.lesson.version,
        )[0]
        _, second = self.ordered_race(self.cancel(row), self.assign(self.students[:1]))
        self.assertEqual(second[0], "ok")
        student_rows = self.rows(student=self.students[0])
        self.assertEqual(student_rows.count(), 2)
        self.assertEqual(student_rows.filter(cancelled_at__isnull=True).count(), 1)
        self.assertEqual(student_rows.filter(cancelled_at__isnull=False).count(), 1)

    def test_double_cancel_applies_once(self):
        row = assignments.create_assignments(
            actor=self.owner, classroom_id=self.room.pk, lesson_id=self.lesson.pk,
            student_ids=[self.students[0].pk], expected_lesson_version=self.lesson.version,
        )[0]
        _, second = self.ordered_race(self.cancel(row), self.cancel(row))
        self.assertEqual(second[0], "invalid")
        row.refresh_from_db()
        self.assertIsNotNone(row.cancelled_at)
        self.assertEqual(row.version, 2)

    def test_archive_commits_before_confirmation(self):
        archive = self.spec(archive_lesson, lesson_id=self.lesson.pk,
                            expected_version=self.lesson.version)
        _, second = self.ordered_race(archive, self.assign())
        self.assertEqual(second[0], "invalid")
        self.assertFalse(self.rows().exists())

    def test_confirmation_commits_before_archive_and_keeps_snapshot(self):
        archive = self.spec(archive_lesson, lesson_id=self.lesson.pk,
                            expected_version=self.lesson.version)
        _, second = self.ordered_race(self.assign(), archive)
        self.assertEqual(second[0], "ok")
        self.lesson.refresh_from_db()
        self.assertFalse(self.lesson.is_active)
        self.assertEqual(self.rows(cancelled_at__isnull=True).count(), 2)
        self.assertEqual(self.rows().filter(title="Synthetic race lesson").count(), 2)


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class AssignmentReviewReplayTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic replay center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="replay-owner", email="replay-owner@example.test",
            role="OWNER", organization=self.org,
        )
        self.owner.is_verified = lambda: True
        self.student = User.objects.create_user(
            username="replay-student", role="STUDENT", organization=self.org,
        )
        StudentProfile.objects.create(user=self.student, grade="4")
        self.room = Classroom.objects.create(
            organization=self.org, created_by=self.owner, name="Replay builders",
        )
        ClassEnrollment.objects.create(classroom=self.room, student=self.student)
        self.lesson = synthetic_lesson(self.owner)
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        self.client.force_login(self.owner)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        self.url = reverse("lessons:assignment-create", args=[self.room.pk])

    def confirm_payload(self):
        response = self.client.post(self.url, {
            "action": "review", "lesson": self.lesson.pk, "students": [self.student.pk],
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LessonAssignment.objects.exists())
        return {"action": "confirm", "token": response.context["form"].initial["token"],
                "confirm": "on"}

    def test_replayed_confirmation_after_success_is_rejected(self):
        payload = self.confirm_payload()
        self.assertEqual(self.client.post(self.url, payload).status_code, 302)
        self.assertEqual(self.client.post(self.url, payload).status_code, 400)
        self.assertEqual(LessonAssignment.objects.count(), 1)

    def test_replay_after_cancellation_creates_nothing(self):
        payload = self.confirm_payload()
        self.assertEqual(self.client.post(self.url, payload).status_code, 302)
        row = LessonAssignment.objects.get()
        assignments.cancel_assignment(
            actor=self.owner, assignment_id=row.pk, expected_version=row.version,
        )
        self.assertEqual(self.client.post(self.url, payload).status_code, 400)
        self.assertEqual(LessonAssignment.objects.count(), 1)
        self.assertEqual(LessonAssignment.objects.filter(cancelled_at__isnull=True).count(), 0)
