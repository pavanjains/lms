from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.lessons.assignments import (
    cancel_assignment,
    create_assignments,
    staff_assignments,
    student_assignments,
)
from apps.lessons.models import LESSON_FIELDS, LessonAssignment
from apps.lessons.services import archive_lesson, create_lesson, update_lesson
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class AssignmentFoundationTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic assignment center")
        self.other_org = Organization.objects.create(name="Other synthetic center")
        self.owner = self.make_user("owner", "OWNER")
        self.teacher = self.make_user("teacher", "INSTRUCTOR")
        self.peer = self.make_user("peer", "INSTRUCTOR")
        self.foreign_owner = self.make_user("foreign-owner", "OWNER", self.other_org)
        self.a = self.make_user("student-a", "STUDENT")
        self.b = self.make_user("student-b", "STUDENT")
        self.room = Classroom.objects.create(
            organization=self.org, created_by=self.owner, name="Builders",
        )
        ClassInstructor.objects.create(classroom=self.room, instructor=self.teacher)
        for student in (self.a, self.b):
            ClassEnrollment.objects.create(classroom=self.room, student=student)
        self.lesson = create_lesson(actor=self.teacher, **self.lesson_data())

    def make_user(self, username, role, organization=None):
        user = get_user_model().objects.create_user(
            username=username, email=username + "@example.test", role=role,
            organization=organization or self.org,
        )
        # Service tests only: real session/MFA integration belongs in HTTP tests.
        user.is_verified = lambda: True
        if role == "STUDENT":
            StudentProfile.objects.create(user=user, grade="4")
        return user

    def lesson_data(self, **changes):
        data = {
            "title": "Synthetic build",
            "summary": "Explore movement",
            "lego_url": "https://education.lego.com/en-us/lessons/synthetic-not-verified/",
            "instructions": "Read and build with your instructor.",
            "kit": "ESSENTIAL", "min_grade": 1, "max_grade": 4,
        }
        return {**data, **changes}

    def assign(self, **changes):
        arguments = {
            "actor": self.teacher, "classroom_id": self.room.pk,
            "lesson_id": self.lesson.pk, "student_ids": [self.a.pk],
            "expected_lesson_version": self.lesson.version,
        }
        return create_assignments(**{**arguments, **changes})

    def test_batch_snapshots_all_lesson_fields_and_explicit_recipients(self):
        rows = self.assign(student_ids=[self.b.pk, self.a.pk])
        self.assertEqual({row.student_id for row in rows}, {self.a.pk, self.b.pk})
        self.assertEqual(LessonAssignment.objects.count(), 2)
        for row in rows:
            with self.subTest(student=row.student_id):
                self.assertEqual(row.organization_id, self.org.pk)
                self.assertEqual(row.classroom_id, self.room.pk)
                self.assertEqual(row.lesson_id, self.lesson.pk)
                self.assertEqual(row.created_by_id, self.teacher.pk)
                self.assertEqual(row.lesson_version, self.lesson.version)
                self.assertEqual(row.version, 1)
                self.assertIsNone(row.cancelled_at)
                self.assertIsNone(row.cancelled_by_id)
                for field in LESSON_FIELDS:
                    self.assertEqual(getattr(row, field), getattr(self.lesson, field))

    def test_new_enrollment_does_not_expand_existing_assignments(self):
        self.assign()
        newcomer = self.make_user("newcomer", "STUDENT")
        ClassEnrollment.objects.create(classroom=self.room, student=newcomer)
        self.assertFalse(student_assignments(newcomer).exists())
        self.assertFalse(student_assignments(self.b).exists())
        self.assertEqual(LessonAssignment.objects.count(), 1)

    def test_grade_four_accepts_either_kit(self):
        for kit in ("ESSENTIAL", "PRIME"):
            with self.subTest(kit=kit):
                lesson = create_lesson(
                    actor=self.teacher, **self.lesson_data(kit=kit, min_grade=4, max_grade=4),
                )
                row = self.assign(lesson_id=lesson.pk)[0]
                self.assertEqual(row.kit, kit)

    def test_prek_and_kindergarten_grade_mapping(self):
        lesson = create_lesson(
            actor=self.teacher, **self.lesson_data(min_grade=-1, max_grade=0),
        )
        StudentProfile.objects.filter(user=self.a).update(grade="PRE_K")
        StudentProfile.objects.filter(user=self.b).update(grade="K")
        rows = self.assign(lesson_id=lesson.pk, student_ids=[self.a.pk, self.b.pk])
        self.assertEqual({row.student_id for row in rows}, {self.a.pk, self.b.pk})

    def test_incompatible_batch_creates_nothing(self):
        StudentProfile.objects.filter(user=self.b).update(grade="5")
        with self.assertRaises(ValidationError):
            self.assign(student_ids=[self.a.pk, self.b.pk])
        self.assertFalse(LessonAssignment.objects.exists())

    def test_prime_rejects_below_grade_four(self):
        lesson = create_lesson(
            actor=self.teacher, **self.lesson_data(kit="PRIME", min_grade=4, max_grade=8),
        )
        StudentProfile.objects.filter(user=self.a).update(grade="3")
        with self.assertRaises(ValidationError):
            self.assign(lesson_id=lesson.pk)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_missing_student_profile_rejected(self):
        StudentProfile.objects.filter(user=self.a).delete()
        with self.assertRaises(ValidationError):
            self.assign()
        self.assertFalse(LessonAssignment.objects.exists())

    def test_recipient_ids_must_be_nonempty_distinct_positive_integers(self):
        cases = ([], (), None, "all", [self.a.pk, self.a.pk], [str(self.a.pk)],
                 [True], [0], [-1], [1.5])
        for ids in cases:
            with self.subTest(ids=ids), self.assertRaises(ValidationError):
                self.assign(student_ids=ids)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_review_version_requires_current_positive_integer(self):
        for version in (None, True, "1", 0, -1, 99):
            with self.subTest(version=version), self.assertRaises(ValidationError):
                self.assign(expected_lesson_version=version)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_lesson_edit_invalidates_reviewed_version(self):
        update_lesson(
            actor=self.teacher, lesson_id=self.lesson.pk, expected_version=1,
            **self.lesson_data(title="Edited after review"),
        )
        with self.assertRaises(ValidationError):
            self.assign(expected_lesson_version=1)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_archived_lesson_cannot_be_assigned(self):
        archived = archive_lesson(
            actor=self.teacher, lesson_id=self.lesson.pk, expected_version=1,
        )
        with self.assertRaises(ValidationError):
            self.assign(expected_lesson_version=archived.version)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_foreign_lesson_class_and_student_denied(self):
        foreign_lesson = create_lesson(actor=self.foreign_owner, **self.lesson_data())
        foreign_student = self.make_user("foreign-student", "STUDENT", self.other_org)
        foreign_room = Classroom.objects.create(
            organization=self.other_org, created_by=self.foreign_owner, name="Other class",
        )
        cases = (
            {"lesson_id": foreign_lesson.pk},
            {"classroom_id": foreign_room.pk},
            {"student_ids": [self.a.pk, foreign_student.pk]},
        )
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(PermissionDenied):
                self.assign(**changes)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_unenrolled_and_inactive_enrollment_recipients_denied(self):
        extra = self.make_user("unenrolled", "STUDENT")
        with self.assertRaises(PermissionDenied):
            self.assign(student_ids=[extra.pk])
        ClassEnrollment.objects.filter(classroom=self.room, student=self.a).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.assign()
        self.assertFalse(LessonAssignment.objects.exists())

    def test_inactive_or_privileged_student_recipient_denied(self):
        User = get_user_model()
        for change in ({"is_active": False}, {"is_staff": True}, {"is_superuser": True}):
            User.objects.filter(pk=self.a.pk).update(
                is_active=True, is_staff=False, is_superuser=False,
            )
            User.objects.filter(pk=self.a.pk).update(**change)
            with self.subTest(change=change), self.assertRaises(PermissionDenied):
                self.assign()
        self.assertFalse(LessonAssignment.objects.exists())

    def test_unassigned_instructor_student_and_foreign_owner_cannot_assign(self):
        for actor in (self.peer, self.a, self.foreign_owner):
            with self.subTest(actor=actor.pk), self.assertRaises(PermissionDenied):
                self.assign(actor=actor)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_owner_can_assign_without_instructor_membership(self):
        row = self.assign(actor=self.owner)[0]
        self.assertEqual(row.created_by_id, self.owner.pk)

    def test_current_mfa_and_staff_feature_flag_required(self):
        self.teacher.is_verified = lambda: False
        with self.assertRaises(PermissionDenied):
            self.assign()
        self.teacher.is_verified = lambda: True
        with self.settings(LMS_STAFF_AUTH_ENABLED=False):
            with self.assertRaises(PermissionDenied):
                self.assign()
        self.assertFalse(LessonAssignment.objects.exists())

    def test_stale_actor_account_and_membership_are_rechecked(self):
        User = get_user_model()
        User.objects.filter(pk=self.teacher.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.assign()
        User.objects.filter(pk=self.teacher.pk).update(is_active=True)
        ClassInstructor.objects.filter(classroom=self.room, instructor=self.teacher).update(
            is_active=False,
        )
        with self.assertRaises(PermissionDenied):
            self.assign()
        self.assertFalse(LessonAssignment.objects.exists())

    def test_inactive_class_or_organization_blocks_assignment(self):
        self.room.is_active = False
        self.room.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            self.assign(actor=self.owner)
        self.room.is_active = True
        self.room.save(update_fields=["is_active"])
        self.org.is_active = False
        self.org.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            self.assign(actor=self.owner)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_duplicate_in_batch_does_not_assign_other_recipient(self):
        original = self.assign()[0]
        with self.assertRaises(ValidationError):
            self.assign(student_ids=[self.a.pk, self.b.pk])
        self.assertEqual(list(LessonAssignment.objects.values_list("pk", flat=True)), [original.pk])
        self.assertFalse(student_assignments(self.b).exists())

    def test_failure_on_second_insert_rolls_back_first_insert(self):
        real_save = LessonAssignment.save
        calls = []

        def fail_second(instance, *args, **kwargs):
            calls.append(instance.student_id)
            if len(calls) == 2:
                raise ValidationError("Synthetic second-insert failure.")
            return real_save(instance, *args, **kwargs)

        with patch.object(LessonAssignment, "save", autospec=True, side_effect=fail_second):
            with self.assertRaises(ValidationError):
                self.assign(student_ids=[self.a.pk, self.b.pk])
        self.assertEqual(len(calls), 2)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_database_rejects_duplicate_active_assignment(self):
        duplicate = self.assign()[0]
        duplicate.pk = None
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save(force_insert=True)
        self.assertEqual(LessonAssignment.objects.count(), 1)

    def test_database_requires_cancellation_pair_and_positive_versions(self):
        row = self.assign()[0]
        for change in (
            {"cancelled_at": timezone.now()},
            {"cancelled_by_id": self.teacher.pk},
            {"version": 0},
            {"lesson_version": 0},
        ):
            with self.subTest(change=change):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    LessonAssignment.objects.filter(pk=row.pk).update(**change)
        row.refresh_from_db()
        self.assertIsNone(row.cancelled_at)
        self.assertIsNone(row.cancelled_by_id)
        self.assertEqual(row.version, 1)
        self.assertEqual(row.lesson_version, 1)

    def test_library_edit_and_archive_preserve_assigned_snapshot(self):
        row = self.assign()[0]
        before = {field: getattr(row, field) for field in LESSON_FIELDS}
        edited = update_lesson(
            actor=self.teacher, lesson_id=self.lesson.pk, expected_version=1,
            **self.lesson_data(
                title="Changed source", summary="Changed summary",
                instructions="Changed instructions", kit="PRIME", min_grade=4, max_grade=8,
            ),
        )
        archive_lesson(actor=self.teacher, lesson_id=edited.pk, expected_version=edited.version)
        row.refresh_from_db()
        self.assertEqual({field: getattr(row, field) for field in LESSON_FIELDS}, before)
        self.assertEqual(row.lesson_version, 1)
        self.assertEqual(student_assignments(self.a).get().pk, row.pk)

    def test_cancellation_checks_actor_class_and_version(self):
        row = self.assign()[0]
        for actor in (self.peer, self.a, self.foreign_owner):
            with self.subTest(actor=actor.pk), self.assertRaises(PermissionDenied):
                cancel_assignment(actor=actor, assignment_id=row.pk, expected_version=1)
        for version in (None, True, "1", 0, 99):
            with self.subTest(version=version), self.assertRaises(ValidationError):
                cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=version)
        row.refresh_from_db()
        self.assertIsNone(row.cancelled_at)
        self.assertEqual(row.version, 1)

    def test_cancellation_retains_history_and_allows_reassignment(self):
        row = self.assign()[0]
        cancelled = cancel_assignment(
            actor=self.teacher, assignment_id=row.pk, expected_version=1,
        )
        self.assertIsNotNone(cancelled.cancelled_at)
        self.assertEqual(cancelled.cancelled_by_id, self.teacher.pk)
        self.assertEqual(cancelled.version, 2)
        self.assertFalse(student_assignments(self.a).exists())
        self.assertTrue(staff_assignments(self.owner).filter(pk=row.pk).exists())
        replacement = self.assign()[0]
        self.assertNotEqual(replacement.pk, row.pk)
        self.assertEqual(LessonAssignment.objects.count(), 2)
        self.assertEqual(student_assignments(self.a).get().pk, replacement.pk)

    def test_stale_cancellation_retry_cannot_change_history(self):
        row = self.assign()[0]
        first = cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=1)
        with self.assertRaises(ValidationError):
            cancel_assignment(actor=self.owner, assignment_id=row.pk, expected_version=1)
        again = cancel_assignment(actor=self.owner, assignment_id=row.pk, expected_version=2)
        self.assertEqual(again.cancelled_at, first.cancelled_at)
        self.assertEqual(again.cancelled_by_id, self.teacher.pk)
        self.assertEqual(again.version, 2)

    def test_student_and_staff_queries_isolate_identity_and_organization(self):
        row = self.assign()[0]
        foreign_student = self.make_user("foreign-reader", "STUDENT", self.other_org)
        self.assertEqual(student_assignments(self.a).get().pk, row.pk)
        self.assertFalse(student_assignments(self.b).exists())
        self.assertFalse(student_assignments(foreign_student).exists())
        self.assertFalse(staff_assignments(self.peer).exists())
        self.assertFalse(staff_assignments(self.foreign_owner).exists())
        self.assertEqual(staff_assignments(self.teacher).get().pk, row.pk)
        with self.assertRaises(PermissionDenied):
            student_assignments(self.teacher)
        with self.assertRaises(PermissionDenied):
            staff_assignments(self.a)

    def test_student_flag_and_deactivated_account_revoke_read_access(self):
        self.assign()
        with self.settings(LMS_STUDENT_AUTH_ENABLED=False):
            with self.assertRaises(PermissionDenied):
                student_assignments(self.a)
        get_user_model().objects.filter(pk=self.a.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            student_assignments(self.a)

    def test_ending_enrollment_revokes_student_access_without_deleting_history(self):
        row = self.assign()[0]
        ClassEnrollment.objects.filter(classroom=self.room, student=self.a).update(is_active=False)
        self.assertFalse(student_assignments(self.a).exists())
        self.assertTrue(LessonAssignment.objects.filter(pk=row.pk).exists())

    def test_removed_instructor_loses_read_and_cancel_access(self):
        row = self.assign()[0]
        ClassInstructor.objects.filter(classroom=self.room, instructor=self.teacher).update(
            is_active=False,
        )
        self.assertFalse(staff_assignments(self.teacher).exists())
        with self.assertRaises(PermissionDenied):
            cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=1)
        self.assertTrue(staff_assignments(self.owner).filter(pk=row.pk).exists())

    def test_archived_class_hides_work_and_only_owner_can_cancel(self):
        row = self.assign()[0]
        self.room.is_active = False
        self.room.save(update_fields=["is_active"])
        self.assertFalse(student_assignments(self.a).exists())
        self.assertFalse(staff_assignments(self.teacher).exists())
        with self.assertRaises(PermissionDenied):
            cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=1)
        cancelled = cancel_assignment(actor=self.owner, assignment_id=row.pk, expected_version=1)
        self.assertIsNotNone(cancelled.cancelled_at)

    def test_inactive_organization_revokes_staff_and_student_reads(self):
        self.assign()
        self.org.is_active = False
        self.org.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            staff_assignments(self.teacher)
        with self.assertRaises(PermissionDenied):
            student_assignments(self.a)

    def test_shared_student_assignments_remain_scoped_by_class(self):
        first = self.assign()[0]
        second_room = Classroom.objects.create(
            organization=self.org, created_by=self.owner, name="Second class",
        )
        ClassInstructor.objects.create(classroom=second_room, instructor=self.peer)
        ClassEnrollment.objects.create(classroom=second_room, student=self.a)
        second = self.assign(actor=self.peer, classroom_id=second_room.pk)[0]
        self.assertEqual(set(student_assignments(self.a).values_list("pk", flat=True)),
                         {first.pk, second.pk})
        self.assertEqual(list(staff_assignments(self.teacher).values_list("pk", flat=True)), [first.pk])
        self.assertEqual(list(staff_assignments(self.peer).values_list("pk", flat=True)), [second.pk])
        with self.assertRaises(PermissionDenied):
            cancel_assignment(actor=self.peer, assignment_id=first.pk, expected_version=1)
