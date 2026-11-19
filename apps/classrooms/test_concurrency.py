from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event
from time import monotonic
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, connections, transaction
from django.test import TransactionTestCase, override_settings

from apps.accounts.deactivation import deactivate_instructor
from apps.accounts.models import StudentProfile
from apps.classrooms import services
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.classrooms.policies import visible_classrooms
from apps.organizations.models import Organization


@skipUnless(connection.vendor == "postgresql", "Requires real PostgreSQL row locks.")
@override_settings(LMS_STAFF_AUTH_ENABLED=True, SESSION_ENGINE="django.contrib.sessions.backends.db")
class ClassroomConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic concurrency center")
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", email="owner@example.test",
                                              role="OWNER", organization=self.org)
        self.teacher = User.objects.create_user(username="teacher", email="teacher@example.test",
                                                role="INSTRUCTOR", organization=self.org)
        self.second = User.objects.create_user(username="second", email="second@example.test",
                                               role="INSTRUCTOR", organization=self.org)
        self.student = User.objects.create_user(username="student", role="STUDENT", organization=self.org)
        StudentProfile.objects.create(user=self.student, grade="4")
        self.source = Classroom.objects.create(organization=self.org, name="Source", created_by=self.owner)
        self.room = Classroom.objects.create(organization=self.org, name="Target", created_by=self.owner)
        for room in (self.source, self.room):
            ClassInstructor.objects.create(classroom=room, instructor=self.teacher)
        ClassEnrollment.objects.create(classroom=self.source, student=self.student)

    def spec(self, function, actor=None, **kwargs):
        return function, (actor or self.owner).pk, kwargs

    def enroll(self, actor=None):
        return self.spec(services.enroll_student, actor,
                         classroom_id=self.room.pk, student_id=self.student.pk)

    def remove(self):
        return self.spec(services.remove_instructor, classroom_id=self.room.pk,
                         instructor_id=self.teacher.pk)

    def archive(self):
        return self.spec(services.archive_classroom, classroom_id=self.room.pk)

    def deactivate(self):
        return self.spec(deactivate_instructor, instructor_id=self.teacher.pk)

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

    def test_duplicate_normalized_class_name(self):
        first, second = self.ordered_race(
            self.spec(services.create_classroom, name="Race"),
            self.spec(services.create_classroom, name=" RACE "),
        )
        self.assertIsNotNone(first[1])
        self.assertEqual(second[0], "invalid")
        self.assertEqual(Classroom.objects.filter(organization=self.org, name__iexact="Race").count(), 1)

    def test_duplicate_instructor_assignment_reuses_row(self):
        operation = self.spec(services.assign_instructor, classroom_id=self.room.pk,
                              instructor_id=self.second.pk)
        first, second = self.ordered_race(operation, operation)
        self.assertEqual(first, second)
        self.assertEqual(ClassInstructor.objects.filter(classroom=self.room, instructor=self.second).count(), 1)

    def test_duplicate_enrollment_reuses_row(self):
        first, second = self.ordered_race(self.enroll(), self.enroll())
        self.assertEqual(first, second)
        self.assertEqual(ClassEnrollment.objects.filter(classroom=self.room, student=self.student).count(), 1)

    def test_membership_removal_wins_before_enrollment(self):
        _, second = self.ordered_race(self.remove(), self.enroll(self.teacher))
        self.assertEqual(second[0], "denied")
        self.assertFalse(ClassEnrollment.objects.filter(classroom=self.room).exists())

    def test_enrollment_commits_before_membership_removal(self):
        _, second = self.ordered_race(self.enroll(self.teacher), self.remove())
        self.assertEqual(second[0], "ok")
        self.assertTrue(ClassEnrollment.objects.get(classroom=self.room, student=self.student).is_active)
        self.teacher.is_verified = lambda: True
        self.assertFalse(visible_classrooms(self.teacher).filter(pk=self.room.pk).exists())

    def test_archive_wins_before_enrollment(self):
        _, second = self.ordered_race(self.archive(), self.enroll())
        self.assertEqual(second[0], "denied")
        self.assertFalse(ClassEnrollment.objects.filter(classroom=self.room).exists())

    def test_enrollment_commits_before_archive(self):
        _, second = self.ordered_race(self.enroll(), self.archive())
        self.assertEqual(second[0], "ok")
        self.room.refresh_from_db()
        self.assertFalse(self.room.is_active)
        self.assertTrue(ClassEnrollment.objects.filter(classroom=self.room, is_active=True).exists())
        self.teacher.is_verified = lambda: True
        self.assertFalse(visible_classrooms(self.teacher).filter(pk=self.room.pk).exists())

    def test_deactivation_wins_before_instructor_write(self):
        _, second = self.ordered_race(self.deactivate(), self.enroll(self.teacher))
        self.assertEqual(second[0], "denied")
        self.teacher.refresh_from_db()
        self.assertFalse(self.teacher.is_active)
        self.assertFalse(ClassEnrollment.objects.filter(classroom=self.room).exists())

    def test_instructor_write_commits_before_deactivation(self):
        _, second = self.ordered_race(self.enroll(self.teacher), self.deactivate())
        self.assertEqual(second[0], "ok")
        self.assertTrue(ClassEnrollment.objects.filter(classroom=self.room, is_active=True).exists())
        self.teacher.is_verified = lambda: True
        with self.assertRaises(PermissionDenied):
            visible_classrooms(self.teacher)

    def test_end_then_reenroll_preserves_relationship(self):
        link = ClassEnrollment.objects.create(classroom=self.room, student=self.student)
        first, second = self.ordered_race(
            self.spec(services.end_enrollment, classroom_id=self.room.pk, student_id=self.student.pk),
            self.enroll(),
        )
        self.assertEqual(first, second)
        self.assertEqual(second[1], link.pk)
        link.refresh_from_db()
        self.assertTrue(link.is_active)

    def test_enroll_then_end_keeps_inactive_relationship(self):
        first, second = self.ordered_race(
            self.enroll(),
            self.spec(services.end_enrollment, classroom_id=self.room.pk, student_id=self.student.pk),
        )
        self.assertEqual(first, second)
        link = ClassEnrollment.objects.get(classroom=self.room, student=self.student)
        self.assertFalse(link.is_active)
