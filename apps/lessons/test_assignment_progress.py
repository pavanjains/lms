from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.classrooms.models import ClassInstructor, Classroom
from apps.lessons import test_assignment_views as staff_views
from apps.lessons import test_assignments as foundation
from apps.lessons.assignments import cancel_assignment, update_progress
from apps.lessons.models import LessonAssignment


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class ProgressServiceTests(TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign

    def update(self, row=None, **changes):
        row = row or self.assign()[0]
        arguments = {"actor": self.teacher, "assignment_id": row.pk, "progress": "IN_PROGRESS",
                     "feedback": "Good start.", "expected_version": row.version}
        return update_progress(**{**arguments, **changes})

    def test_new_assignment_defaults_to_assigned_with_no_feedback(self):
        row = self.assign()[0]
        self.assertEqual(row.progress, "ASSIGNED")
        self.assertEqual(row.feedback, "")
        self.assertIsNone(row.progress_updated_at)
        self.assertIsNone(row.progress_updated_by_id)

    def test_instructor_updates_progress_feedback_and_version(self):
        updated = self.update()
        self.assertEqual(updated.progress, "IN_PROGRESS")
        self.assertEqual(updated.feedback, "Good start.")
        self.assertEqual(updated.version, 2)
        self.assertEqual(updated.progress_updated_by_id, self.teacher.pk)
        self.assertIsNotNone(updated.progress_updated_at)

    def test_every_allowed_status_is_accepted_in_any_order(self):
        row = self.assign()[0]
        for status in ("REVIEWED", "NEEDS_REVISION", "IN_PROGRESS", "ASSIGNED"):
            with self.subTest(status=status):
                row = self.update(row, progress=status, expected_version=row.version)
                self.assertEqual(row.progress, status)

    def test_owner_can_update_without_instructor_membership(self):
        row = self.update(actor=self.owner)
        self.assertEqual(row.progress_updated_by_id, self.owner.pk)

    def test_feedback_is_stripped_and_may_be_blank(self):
        row = self.update(feedback="  Nice work.  ")
        self.assertEqual(row.feedback, "Nice work.")
        row = self.update(row, feedback="", expected_version=row.version)
        self.assertEqual(row.feedback, "")

    def test_invalid_status_feedback_and_version_are_rejected_without_change(self):
        row = self.assign()[0]
        cases = (
            {"progress": "DONE"}, {"progress": ""}, {"progress": None}, {"progress": 1},
            {"feedback": None}, {"feedback": 5}, {"feedback": "x" * 2001},
            {"expected_version": None}, {"expected_version": True},
            {"expected_version": "1"}, {"expected_version": 0}, {"expected_version": 99},
        )
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.update(row, **changes)
        row.refresh_from_db()
        self.assertEqual((row.progress, row.feedback, row.version), ("ASSIGNED", "", 1))

    def test_stale_version_cannot_overwrite_a_newer_update(self):
        row = self.assign()[0]
        self.update(row, feedback="First.")
        with self.assertRaises(ValidationError):
            self.update(row, actor=self.owner, feedback="Stale.", expected_version=1)
        row.refresh_from_db()
        self.assertEqual((row.feedback, row.version), ("First.", 2))

    def test_unassigned_instructor_student_and_foreign_owner_denied(self):
        row = self.assign()[0]
        for actor in (self.peer, self.a, self.foreign_owner):
            with self.subTest(actor=actor.pk), self.assertRaises(PermissionDenied):
                self.update(row, actor=actor)
        row.refresh_from_db()
        self.assertEqual(row.progress, "ASSIGNED")

    def test_removed_instructor_and_inactive_class_are_denied(self):
        row = self.assign()[0]
        ClassInstructor.objects.filter(classroom=self.room, instructor=self.teacher).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.update(row)
        Classroom.objects.filter(pk=self.room.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.update(row, actor=self.owner)
        row.refresh_from_db()
        self.assertEqual(row.version, 1)

    def test_cancelled_assignment_cannot_change_progress(self):
        row = self.assign()[0]
        cancelled = cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=1)
        with self.assertRaises(ValidationError):
            self.update(cancelled, expected_version=cancelled.version)
        cancelled.refresh_from_db()
        self.assertEqual(cancelled.progress, "ASSIGNED")

    def test_progress_update_keeps_snapshot_and_advances_cancel_version(self):
        row = self.assign()[0]
        title = row.title
        updated = self.update(row)
        self.assertEqual(updated.title, title)
        cancelled = cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=2)
        self.assertEqual(cancelled.version, 3)
        self.assertEqual(cancelled.progress, "IN_PROGRESS")

    def test_database_rejects_unknown_status_and_unpaired_update_fields(self):
        row = self.assign()[0]
        for change in ({"progress": "DONE"}, {"progress_updated_at": timezone.now()},
                       {"progress_updated_by_id": self.teacher.pk}):
            with self.subTest(change=change):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    LessonAssignment.objects.filter(pk=row.pk).update(**change)
        row.refresh_from_db()
        self.assertEqual(row.progress, "ASSIGNED")


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class ProgressViewTests(TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign
    login_staff = staff_views.InstructorAssignmentViewsTests.login_staff
    password = "Synthetic-Student-UI-Only!7349"

    def progress_url(self, row):
        return reverse("lessons:assignment-progress", args=[row.pk])

    def detail_url(self, row):
        return reverse("lessons:assignment-detail", args=[row.pk])

    def payload(self, row, **changes):
        data = {"expected_version": row.version, "progress": "NEEDS_REVISION",
                "feedback": "Please rebuild the gearbox.", "confirm": "on"}
        return {**data, **changes}

    def student_client(self):
        self.a.set_password(self.password)
        self.a.save(update_fields=["password"])
        client = Client()
        client.post(reverse("student-login"), {"student_username": self.a.username,
                                               "password": self.password})
        return client

    def test_post_saves_progress_and_staff_detail_shows_feedback(self):
        row = self.assign()[0]
        self.login_staff()
        response = self.client.post(self.progress_url(row), self.payload(row))
        self.assertRedirects(response, self.detail_url(row))
        row.refresh_from_db()
        self.assertEqual((row.progress, row.feedback, row.version),
                         ("NEEDS_REVISION", "Please rebuild the gearbox.", 2))
        page = self.client.get(self.detail_url(row))
        self.assertContains(page, "Needs revision")
        self.assertContains(page, "Please rebuild the gearbox.")
        self.assertContains(page, "Update progress and feedback")

    def test_get_and_other_methods_are_rejected(self):
        row = self.assign()[0]
        self.login_staff()
        for method in ("GET", "PUT", "PATCH", "DELETE"):
            with self.subTest(method=method):
                self.assertEqual(self.client.generic(method, self.progress_url(row)).status_code, 405)
        row.refresh_from_db()
        self.assertEqual(row.version, 1)

    def test_missing_confirmation_bad_status_and_stale_version_do_not_save(self):
        row = self.assign()[0]
        self.login_staff()
        for changes in ({"confirm": ""}, {"progress": "DONE"}, {"expected_version": 99},
                        {"feedback": "x" * 2001}):
            with self.subTest(changes=changes):
                self.assertEqual(self.client.post(self.progress_url(row),
                                                  self.payload(row, **changes)).status_code, 400)
        row.refresh_from_db()
        self.assertEqual((row.progress, row.version), ("ASSIGNED", 1))

    def test_feedback_is_escaped_on_staff_pages(self):
        row = self.assign()[0]
        self.login_staff()
        self.client.post(self.progress_url(row), self.payload(row, feedback="<script>bad()</script>"))
        page = self.client.get(self.detail_url(row))
        self.assertContains(page, "&lt;script&gt;")
        self.assertNotContains(page, "<script>bad()")

    def test_unassigned_instructor_and_foreign_owner_get_not_found(self):
        row = self.assign()[0]
        for user in (self.peer, self.foreign_owner):
            with self.subTest(user=user.pk):
                client = Client()
                self.login_staff(user, client)
                self.assertEqual(client.post(self.progress_url(row), self.payload(row)).status_code, 404)
        row.refresh_from_db()
        self.assertEqual(row.progress, "ASSIGNED")

    def test_anonymous_and_student_sessions_cannot_write_progress(self):
        row = self.assign()[0]
        self.assertEqual(self.client.post(self.progress_url(row), self.payload(row)).status_code, 302)
        student = self.student_client()
        self.assertEqual(student.post(self.progress_url(row), self.payload(row)).status_code, 403)
        row.refresh_from_db()
        self.assertEqual((row.progress, row.version), ("ASSIGNED", 1))

    def test_cancelled_assignment_hides_progress_form_and_rejects_post(self):
        row = self.assign()[0]
        self.login_staff()
        cancelled = cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=1)
        self.assertNotContains(self.client.get(self.detail_url(row)), "Update progress and feedback")
        self.assertEqual(self.client.post(self.progress_url(row),
                                          self.payload(cancelled)).status_code, 400)

    def test_csrf_is_enforced(self):
        row = self.assign()[0]
        client = Client(enforce_csrf_checks=True)
        self.login_staff(client=client)
        self.assertEqual(client.post(self.progress_url(row), self.payload(row)).status_code, 403)
        row.refresh_from_db()
        self.assertEqual(row.version, 1)

    def test_student_sees_status_only_and_never_feedback(self):
        row = self.assign()[0]
        student = self.student_client()
        self.login_staff()
        secret = "Private instructor note about behavior."
        self.client.post(self.progress_url(row), self.payload(row, progress="REVIEWED", feedback=secret))
        for url in (reverse("student-assignment-list"),
                    reverse("student-assignment-detail", args=[row.pk])):
            with self.subTest(url=url):
                page = student.get(url)
                self.assertEqual(page.status_code, 200)
                self.assertContains(page, "Status: Reviewed")
                self.assertNotContains(page, secret)

    def test_student_status_defaults_to_assigned_and_has_no_progress_controls(self):
        row = self.assign()[0]
        student = self.student_client()
        page = student.get(reverse("student-assignment-detail", args=[row.pk]))
        self.assertContains(page, "Status: Assigned")
        self.assertNotContains(page, 'name="progress"')
        self.assertNotContains(page, 'name="feedback"')
        self.assertEqual(student.post(self.progress_url(row), self.payload(row)).status_code, 403)
