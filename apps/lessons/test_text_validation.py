from unittest.mock import patch

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings

from apps.lessons import test_assignments as foundation
from apps.lessons.models import LESSON_FIELDS, Lesson, LessonAssignment
from apps.lessons.services import create_lesson, update_lesson
from apps.lessons.text_validation import validate_lesson_text


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class LessonTextValidationTests(TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign

    def boundary_data(self, **changes):
        return self.lesson_data(**{"summary": "s" * 2000, "instructions": "i" * 20000, **changes})

    def oversized_cases(self):
        return ({"summary": "s" * 2001}, {"instructions": "i" * 20001},
                {"summary": "s" * 2001, "instructions": "i" * 20001})

    def stored_lesson(self):
        return Lesson.objects.values(*LESSON_FIELDS, "version", "updated_at").get(pk=self.lesson.pk)

    def test_create_accepts_exact_limits_without_truncation(self):
        row = create_lesson(actor=self.teacher, **self.boundary_data())
        row.refresh_from_db()
        self.assertEqual(row.summary, "s" * 2000)
        self.assertEqual(row.instructions, "i" * 20000)
        self.assertEqual(row.version, 1)

    def test_create_rejects_oversized_fields_without_insert(self):
        before = list(Lesson.objects.values_list("pk", flat=True))
        for changes in self.oversized_cases():
            with self.subTest(fields=sorted(changes)):
                with self.assertRaises(ValidationError) as caught:
                    create_lesson(actor=self.teacher, **self.lesson_data(**changes))
                self.assertTrue(set(changes).issubset(caught.exception.error_dict))
                self.assertEqual(list(Lesson.objects.values_list("pk", flat=True)), before)

    def test_edit_accepts_exact_limits_and_increments_once(self):
        row = update_lesson(actor=self.teacher, lesson_id=self.lesson.pk,
                            expected_version=1, **self.boundary_data())
        row.refresh_from_db()
        self.assertEqual(row.summary, "s" * 2000)
        self.assertEqual(row.instructions, "i" * 20000)
        self.assertEqual(row.version, 2)

    def test_rejected_edit_preserves_fields_version_and_timestamp(self):
        before = self.stored_lesson()
        for changes in self.oversized_cases():
            with self.subTest(fields=sorted(changes)):
                with self.assertRaises(ValidationError):
                    update_lesson(actor=self.teacher, lesson_id=self.lesson.pk,
                                  expected_version=1,
                                  **self.lesson_data(title="Must not persist", **changes))
                self.assertEqual(self.stored_lesson(), before)
                self.assertFalse(LessonAssignment.objects.exists())

    def test_assignment_copies_exact_boundary_content_to_every_recipient(self):
        self.lesson = update_lesson(actor=self.teacher, lesson_id=self.lesson.pk,
                                    expected_version=1, **self.boundary_data())
        rows = self.assign(student_ids=[self.a.pk, self.b.pk])
        self.assertEqual({row.student_id for row in rows}, {self.a.pk, self.b.pk})
        for row in rows:
            row.refresh_from_db()
            self.assertEqual(row.summary, self.lesson.summary)
            self.assertEqual(row.instructions, self.lesson.instructions)
            self.assertEqual(row.lesson_version, 2)

    def test_assignment_revalidates_oversized_source_and_rejects_entire_batch(self):
        original = {"summary": self.lesson.summary, "instructions": self.lesson.instructions}
        for changes in self.oversized_cases():
            with self.subTest(fields=sorted(changes)):
                Lesson.objects.filter(pk=self.lesson.pk).update(**{**original, **changes})
                with self.assertRaises(ValidationError) as caught:
                    self.assign(student_ids=[self.a.pk, self.b.pk])
                self.assertTrue(set(changes).issubset(caught.exception.error_dict))
                self.assertFalse(LessonAssignment.objects.exists())

    def test_second_invalid_snapshot_rolls_back_first_insert(self):
        real_clean = LessonAssignment.full_clean
        observed_counts = []

        def corrupt_second(instance, *args, **kwargs):
            observed_counts.append(LessonAssignment.objects.count())
            if len(observed_counts) == 2:
                instance.instructions = "i" * 20001
            return real_clean(instance, *args, **kwargs)

        with patch.object(LessonAssignment, "full_clean", autospec=True, side_effect=corrupt_second):
            with self.assertRaises(ValidationError):
                self.assign(student_ids=[self.a.pk, self.b.pk])
        self.assertEqual(observed_counts, [0, 1])
        self.assertFalse(LessonAssignment.objects.exists())
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.version, 1)

    def test_shared_validator_reports_both_fields_on_each_model(self):
        for model in (Lesson, LessonAssignment):
            with self.subTest(model=model.__name__):
                row = model(summary="s" * 2001, instructions="i" * 20001)
                with self.assertRaises(ValidationError) as caught:
                    validate_lesson_text(row)
                self.assertEqual(set(caught.exception.error_dict), {"summary", "instructions"})
                for errors in caught.exception.error_dict.values():
                    self.assertEqual(errors[0].code, "max_length")

    def test_shared_validator_uses_each_models_declared_limits_without_mutation(self):
        for model in (Lesson, LessonAssignment):
            with self.subTest(model=model.__name__):
                summary_limit = model._meta.get_field("summary").max_length
                instructions_limit = model._meta.get_field("instructions").max_length
                self.assertEqual((summary_limit, instructions_limit), (2000, 20000))
                row = model(summary="s" * summary_limit, instructions="i" * instructions_limit)
                validate_lesson_text(row)
                self.assertEqual((len(row.summary), len(row.instructions)), (2000, 20000))

    def test_existing_instruction_trimming_and_summary_whitespace_are_preserved(self):
        row = create_lesson(actor=self.teacher, **self.lesson_data(
            summary=" " + "s" * 1999, instructions="  " + "i" * 20000 + "  ",
        ))
        row.refresh_from_db()
        self.assertEqual(row.summary, " " + "s" * 1999)
        self.assertEqual(row.instructions, "i" * 20000)
        blank_summary = create_lesson(actor=self.teacher, **self.lesson_data(summary=""))
        self.assertEqual(blank_summary.summary, "")

    def test_unicode_limits_count_characters_not_encoded_bytes(self):
        row = create_lesson(actor=self.teacher, **self.lesson_data(
            summary="é" * 2000, instructions="界" * 20000,
        ))
        row.refresh_from_db()
        self.assertEqual((len(row.summary), len(row.instructions)), (2000, 20000))
        with self.assertRaises(ValidationError):
            create_lesson(actor=self.teacher, **self.lesson_data(summary="é" * 2001))

    def test_unauthorized_calls_still_fail_before_new_text_validation(self):
        data = self.lesson_data(summary="s" * 2001)
        with self.assertRaises(PermissionDenied):
            create_lesson(actor=self.a, **data)
        with self.assertRaises(PermissionDenied):
            update_lesson(actor=self.peer, lesson_id=self.lesson.pk, expected_version=1, **data)
        with self.assertRaises(PermissionDenied):
            self.assign(actor=self.peer)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(self.stored_lesson()["version"], 1)
        self.assertFalse(LessonAssignment.objects.exists())
