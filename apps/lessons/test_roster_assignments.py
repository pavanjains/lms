from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.lessons import test_assignment_views as view_tests
from apps.lessons import test_assignments as foundation
from apps.lessons.assignment_views import REVIEW_KEY, REVIEW_SALT
from apps.lessons.assignments import cancel_assignment, student_assignments
from apps.lessons.models import LessonAssignment
from apps.lessons.services import create_lesson, update_lesson


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class RosterAssignmentTests(TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign
    login_staff = view_tests.InstructorAssignmentViewsTests.login_staff

    def url(self):
        return reverse("lessons:assignment-create", args=[self.room.pk])

    def room_url(self):
        return reverse("classrooms:detail", args=[self.room.pk])

    def select(self, **changes):
        return self.client.post(self.url(), {
            "action": "select-students", "from_roster": "1",
            "students": [self.a.pk], **changes,
        })

    def review(self, **changes):
        response = self.client.post(self.url(), {
            "action": "review", "from_roster": "1", "lesson": self.lesson.pk,
            "students": [self.a.pk], **changes,
        })
        self.assertEqual(response.status_code, 200)
        return response.context["form"].initial["token"]

    def confirm(self, token, **changes):
        return self.client.post(self.url(), {
            "action": "confirm", "token": token, "confirm": "on", **changes,
        })

    def test_roster_entry_preselects_without_creating_and_confirmation_returns_to_class(self):
        self.login_staff()
        roster = self.client.get(self.room_url())
        self.assertContains(roster, "Select all eligible students on this page")
        self.assertContains(roster, 'name="from_roster" value="1"')
        response = self.select()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["students"], [self.a.pk])
        self.assertFalse(LessonAssignment.objects.exists())
        token = self.review()
        self.assertFalse(LessonAssignment.objects.exists())
        self.assertTrue(signing.loads(token, salt=REVIEW_SALT)["from_roster"])
        result = self.confirm(token, students=[self.b.pk], lesson=999, from_roster="0")
        self.assertRedirects(result, self.room_url())
        self.assertEqual(list(LessonAssignment.objects.values_list("student_id", flat=True)), [self.a.pk])
        self.assertTrue(student_assignments(self.a).exists())
        self.assertFalse(student_assignments(self.b).exists())
        self.assertNotIn(REVIEW_KEY, self.client.session)
        self.assertEqual(self.confirm(token).status_code, 400)
        self.assertEqual(LessonAssignment.objects.count(), 1)

    def test_empty_duplicate_foreign_unenrolled_inactive_and_privileged_selections_rejected(self):
        self.login_staff()
        foreign = self.make_user("foreign-roster", "STUDENT", self.other_org)
        outsider = self.make_user("unenrolled-roster", "STUDENT")
        for ids in ([], [self.a.pk, self.a.pk], [foreign.pk], [outsider.pk], ["bad"]):
            with self.subTest(ids=ids):
                self.assertEqual(self.select(students=ids).status_code, 400)
        for changes in ({"is_active": False}, {"is_staff": True}, {"is_superuser": True}):
            get_user_model().objects.filter(pk=self.a.pk).update(**changes)
            self.assertEqual(self.select().status_code, 400)
            get_user_model().objects.filter(pk=self.a.pk).update(
                is_active=True, is_staff=False, is_superuser=False,
            )
        ClassEnrollment.objects.filter(classroom=self.room, student=self.a).update(is_active=False)
        self.assertEqual(self.select().status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_grade_error_and_duplicate_batch_identify_students_without_partial_creation(self):
        self.login_staff()
        StudentProfile.objects.filter(user=self.b).update(grade="5")
        data = {"action": "review", "from_roster": "1", "lesson": self.lesson.pk,
                "students": [self.a.pk, self.b.pk]}
        response = self.client.post(self.url(), data)
        self.assertContains(response, str(self.b), status_code=400)
        self.assertFalse(LessonAssignment.objects.exists())
        StudentProfile.objects.filter(user=self.b).update(grade="4")
        original = self.assign()[0]
        response = self.client.post(self.url(), data)
        self.assertContains(response, "already have this active assignment", status_code=400)
        self.assertEqual(list(LessonAssignment.objects.values_list("pk", flat=True)), [original.pk])

    def test_change_selection_preserves_lesson_and_students_and_invalidates_old_review(self):
        self.login_staff()
        token = self.review()
        response = self.select(lesson=self.lesson.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["lesson"], self.lesson.pk)
        self.assertEqual(response.context["form"].initial["students"], [self.a.pk])
        self.assertEqual(self.confirm(token).status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_cancel_consumes_review_without_assigning(self):
        self.login_staff()
        token = self.review()
        self.assertRedirects(self.client.post(self.url(), {"action": "cancel"}), self.room_url())
        self.assertNotIn(REVIEW_KEY, self.client.session)
        self.assertEqual(self.confirm(token).status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_final_checkbox_and_signed_token_still_required(self):
        self.login_staff()
        token = self.review()
        self.assertEqual(self.confirm(token, confirm="").status_code, 400)
        self.assertEqual(self.confirm(token + "x").status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_stale_lesson_and_revoked_enrollment_block_whole_batch(self):
        self.login_staff()
        token = self.review(students=[self.a.pk, self.b.pk])
        self.lesson = update_lesson(actor=self.teacher, lesson_id=self.lesson.pk,
                                   expected_version=self.lesson.version,
                                   **self.lesson_data(title="Changed roster lesson"))
        self.assertEqual(self.confirm(token).status_code, 400)
        token = self.review(students=[self.a.pk, self.b.pk])
        ClassEnrollment.objects.filter(classroom=self.room, student=self.b).update(is_active=False)
        self.assertEqual(self.confirm(token).status_code, 403)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_class_authorization_rechecked_at_entry_and_confirmation(self):
        for user in (self.peer, self.foreign_owner):
            self.login_staff(user)
            self.assertEqual(self.client.get(self.room_url()).status_code, 404)
            self.assertEqual(self.select().status_code, 404)
        self.login_staff()
        token = self.review()
        ClassInstructor.objects.filter(classroom=self.room, instructor=self.teacher).update(is_active=False)
        self.assertEqual(self.confirm(token).status_code, 404)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_archived_class_has_no_roster_action_and_cannot_assign(self):
        self.room.is_active = False
        self.room.save(update_fields=["is_active"])
        self.login_staff(self.owner)
        self.assertNotContains(self.client.get(self.room_url()), 'id="roster-assignment"')
        self.assertEqual(self.select().status_code, 404)

    def test_history_is_class_scoped_retains_cancellation_and_hides_feedback(self):
        row = self.assign()[0]
        LessonAssignment.objects.filter(pk=row.pk).update(feedback="PRIVATE-ROSTER-NOTE")
        other_room = Classroom.objects.create(organization=self.org, created_by=self.owner, name="Other")
        ClassInstructor.objects.create(classroom=other_room, instructor=self.teacher)
        ClassEnrollment.objects.create(classroom=other_room, student=self.b)
        other = self.assign(classroom_id=other_room.pk, student_ids=[self.b.pk])[0]
        cancel_assignment(actor=self.teacher, assignment_id=row.pk, expected_version=1)
        self.login_staff()
        response = self.client.get(self.room_url())
        self.assertEqual([item.pk for item in response.context["assignments"]], [row.pk])
        self.assertContains(response, "Cancelled")
        self.assertNotContains(response, "PRIVATE-ROSTER-NOTE")
        self.assertNotContains(response, reverse("lessons:assignment-detail", args=[other.pk]))
        self.assertContains(self.client.get(reverse("lessons:assignment-list")),
                            reverse("lessons:assignment-detail", args=[other.pk]))
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")

    def test_roster_and_history_pagination_are_independent(self):
        for n in range(21):
            student = self.make_user(f"roster-extra-{n:02}", "STUDENT")
            ClassEnrollment.objects.create(classroom=self.room, student=student)
            self.assign(student_ids=[student.pk])
        self.login_staff()
        response = self.client.get(self.room_url(), {"page": 2, "assignments_page": 1})
        self.assertEqual(response.context["students"].number, 2)
        self.assertEqual(response.context["assignments"].number, 1)
        self.assertEqual(len(response.context["students"]), 3)
        self.assertEqual(len(response.context["assignments"]), 20)
        self.assertContains(response, "assignments_page=2")
        self.assertFalse(LessonAssignment.objects.filter(student=self.a).exists())

    def test_csrf_and_method_guards_apply_to_roster_entry_and_cancel(self):
        client = Client(enforce_csrf_checks=True)
        self.login_staff(client=client)
        for action in ("select-students", "cancel"):
            self.assertEqual(client.post(self.url(), {"action": action, "students": [self.a.pk]}).status_code, 403)
        self.assertRedirects(self.client.put(self.url()), reverse("two_factor:login"),
                             fetch_redirect_response=False)
        self.client.force_login(self.teacher)
        self.assertRedirects(self.client.put(self.url()), reverse("two_factor:login"),
                             fetch_redirect_response=False)
        self.login_staff()
        self.assertEqual(self.client.put(self.url()).status_code, 405)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_central_entry_keeps_existing_return_destination(self):
        self.login_staff()
        token = self.review(from_roster="0")
        self.assertRedirects(self.confirm(token, from_roster="1"), reverse("lessons:assignment-list"))

    def test_roster_review_expiry_replacement_and_other_session_are_rejected(self):
        self.login_staff()
        first = self.review()
        self.review(students=[self.b.pk])
        self.assertEqual(self.confirm(first).status_code, 400)
        token = self.review()
        other = Client()
        self.login_staff(client=other)
        self.assertEqual(other.post(self.url(), {
            "action": "confirm", "token": token, "confirm": "on",
        }).status_code, 400)
        data = signing.loads(token, salt=REVIEW_SALT)
        with patch.object(signing.TimestampSigner, "timestamp", return_value="0"):
            expired = signing.dumps(data, salt=REVIEW_SALT)
        session = self.client.session
        session[REVIEW_KEY] = expired
        session.save()
        self.assertEqual(self.confirm(expired).status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())

    def test_inactive_or_foreign_lesson_is_not_accepted(self):
        self.login_staff()
        foreign = create_lesson(actor=self.foreign_owner, **self.lesson_data())
        for lesson_id in (foreign.pk, 999999):
            response = self.client.post(self.url(), {
                "action": "review", "from_roster": "1", "lesson": lesson_id,
                "students": [self.a.pk],
            })
            self.assertEqual(response.status_code, 400)
        self.lesson.is_active = False
        self.lesson.save(update_fields=["is_active"])
        response = self.client.post(self.url(), {
            "action": "review", "from_roster": "1", "lesson": self.lesson.pk,
            "students": [self.a.pk],
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(LessonAssignment.objects.exists())
