import time

from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import StudentProfile
from apps.accounts.students import SEEN, STARTED, STUDENT_BACKEND
from apps.classrooms.credential_services import reset_student_credentials
from apps.classrooms.models import ClassEnrollment, Classroom
from apps.lessons import test_assignments as foundation
from apps.lessons.assignments import cancel_assignment
from apps.lessons.models import LessonAssignment
from apps.lessons.services import archive_lesson, create_lesson, update_lesson
from apps.organizations.models import Organization


@override_settings(LMS_STUDENT_AUTH_ENABLED=True, LMS_STAFF_AUTH_ENABLED=True)
class StudentAssignmentViewsTests(TestCase):
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign
    password = "Synthetic-Student-UI-Only!7349"

    def setUp(self):
        foundation.AssignmentFoundationTests.setUp(self)
        for user in (self.a, self.b):
            user.set_password(self.password)
            user.save(update_fields=["password"])
        self.row = self.assign()[0]
        self.list_url = reverse("student-assignment-list")
        self.detail_url = reverse("student-assignment-detail", args=[self.row.pk])

    def sign_in(self, user=None, client=None, password=None):
        client = client or self.client
        response = client.post(reverse("student-login"), {
            "student_username": (user or self.a).username,
            "password": password or self.password,
        })
        self.assertEqual(response.status_code, 302)
        return response

    def test_workspace_links_to_read_only_list_and_snapshot_detail(self):
        self.sign_in()
        self.assertContains(self.client.get(reverse("student-home")), self.list_url)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.row.title)
        self.assertContains(response, self.detail_url)
        self.assertContains(response, "Status: Assigned")
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.row.instructions)
        self.assertNotContains(response, "/documents/")
        self.assertNotContains(response, 'name="status"')
        self.assertNotContains(response, 'name="confirm"')

    def test_cross_student_and_unknown_assignment_ids_are_not_found(self):
        self.sign_in(self.b)
        self.assertContains(self.client.get(self.list_url), "No assigned lessons available")
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)
        unknown = reverse("student-assignment-detail", args=[999999])
        self.assertEqual(self.client.get(unknown).status_code, 404)

    def test_query_parameters_cannot_select_another_student(self):
        self.sign_in(self.b)
        query = {"student_id": self.a.pk, "organization_id": str(self.org.pk),
                 "assignment_id": self.row.pk}
        self.assertNotContains(self.client.get(self.list_url, query), self.row.title)
        self.assertEqual(self.client.get(self.detail_url, query).status_code, 404)

    def test_cross_organization_assignment_is_not_visible(self):
        student = self.make_user("foreign-student", "STUDENT", self.other_org)
        room = Classroom.objects.create(
            organization=self.other_org, created_by=self.foreign_owner, name="Foreign class",
        )
        ClassEnrollment.objects.create(classroom=room, student=student)
        lesson = create_lesson(actor=self.foreign_owner, **self.lesson_data(title="Foreign private lesson"))
        row = self.assign(actor=self.foreign_owner, classroom_id=room.pk,
                          lesson_id=lesson.pk, student_ids=[student.pk],
                          expected_lesson_version=lesson.version)[0]
        self.sign_in()
        self.assertNotContains(self.client.get(self.list_url), lesson.title)
        self.assertEqual(self.client.get(reverse("student-assignment-detail", args=[row.pk])).status_code, 404)

    def test_cancelled_assignment_disappears_but_history_remains(self):
        self.sign_in()
        cancel_assignment(actor=self.teacher, assignment_id=self.row.pk, expected_version=1)
        self.assertNotContains(self.client.get(self.list_url), self.row.title)
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)
        self.assertTrue(LessonAssignment.objects.filter(pk=self.row.pk).exists())

    def test_ended_enrollment_and_archived_class_revoke_access(self):
        self.sign_in()
        link = ClassEnrollment.objects.get(classroom=self.room, student=self.a)
        link.is_active = False
        link.save(update_fields=["is_active"])
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)
        self.assertNotContains(self.client.get(self.list_url), self.row.title)
        link.is_active = True
        link.save(update_fields=["is_active"])
        Classroom.objects.filter(pk=self.room.pk).update(is_active=False)
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_other_class_enrollment_does_not_restore_revoked_assignment_scope(self):
        room = Classroom.objects.create(organization=self.org, created_by=self.owner, name="Second class")
        ClassEnrollment.objects.create(classroom=room, student=self.a)
        row = self.assign(actor=self.owner, classroom_id=room.pk)[0]
        ClassEnrollment.objects.filter(classroom=self.room, student=self.a).update(is_active=False)
        self.sign_in()
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)
        self.assertEqual(self.client.get(reverse("student-assignment-detail", args=[row.pk])).status_code, 200)

    def test_source_edit_and_archive_do_not_replace_assigned_content(self):
        changed = update_lesson(actor=self.teacher, lesson_id=self.lesson.pk, expected_version=1,
                                **self.lesson_data(title="Changed source only", instructions="New source only"))
        archive_lesson(actor=self.teacher, lesson_id=changed.pk, expected_version=changed.version)
        self.sign_in()
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.row.title)
        self.assertContains(response, self.row.instructions)
        self.assertNotContains(response, "New source only")

    def test_rendering_escapes_text_and_does_not_link_invalid_stored_url(self):
        LessonAssignment.objects.filter(pk=self.row.pk).update(
            instructions="<script>synthetic()</script>", lego_url="javascript:alert(1)",
        )
        self.sign_in()
        response = self.client.get(self.detail_url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")
        self.assertNotContains(response, "javascript:")
        self.assertNotContains(response, "Open LEGO instructions")

    def test_all_assignment_mutation_methods_are_rejected_without_state_change(self):
        self.sign_in()
        for url in (self.list_url, self.detail_url):
            for method in ("POST", "PUT", "PATCH", "DELETE"):
                with self.subTest(url=url, method=method):
                    self.assertEqual(self.client.generic(method, url).status_code, 405)
        self.row.refresh_from_db()
        self.assertEqual(self.row.version, 1)
        self.assertIsNone(self.row.cancelled_at)
        self.assertEqual(LessonAssignment.objects.count(), 1)

    def test_list_detail_and_not_found_responses_are_private_no_store(self):
        self.sign_in()
        for url in (self.list_url, self.detail_url,
                    reverse("student-assignment-detail", args=[999999])):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn("private", response["Cache-Control"])
                self.assertIn("no-store", response["Cache-Control"])
                self.assertEqual(response["Referrer-Policy"], "same-origin")

    def test_staff_and_anonymous_sessions_cannot_read_student_assignments(self):
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.owner, backend="apps.accounts.backends.StaffEmailBackend")
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.get(url).status_code, 403)

    def test_missing_timestamps_idle_and_absolute_expiry_fail_closed(self):
        idle, absolute_limit = settings.LMS_STUDENT_IDLE_SECONDS, settings.LMS_STUDENT_ABSOLUTE_SECONDS
        self.client.force_login(self.a, backend=STUDENT_BACKEND)
        self.assertEqual(self.client.get(self.detail_url).status_code, 302)
        for absolute in (False, True):
            self.sign_in()
            session = self.client.session
            now = time.time()
            session[STARTED] = now - ((absolute_limit + 1) if absolute else (idle + 1000))
            session[SEEN] = now - (1 if absolute else (idle + 1))
            session.save()
            self.assertEqual(self.client.get(self.detail_url).status_code, 302)
            self.assertNotIn(SESSION_KEY, self.client.session)

    def test_account_organization_role_profile_and_privilege_revocation(self):
        User = get_user_model()
        for case in ("account", "organization", "role", "profile", "privilege"):
            with self.subTest(case=case):
                self.sign_in()
                if case == "organization":
                    Organization.objects.filter(pk=self.org.pk).update(is_active=False)
                elif case == "profile":
                    StudentProfile.objects.filter(user=self.a).delete()
                else:
                    changes = {"account": {"is_active": False}, "role": {"role": "INSTRUCTOR"},
                               "privilege": {"is_staff": True}}[case]
                    User.objects.filter(pk=self.a.pk).update(**changes)
                self.assertEqual(self.client.get(self.detail_url).status_code, 302)
                User.objects.filter(pk=self.a.pk).update(is_active=True, role="STUDENT", is_staff=False)
                Organization.objects.filter(pk=self.org.pk).update(is_active=True)
                if case == "profile":
                    StudentProfile.objects.create(user=self.a, grade="4")

    def test_logout_then_student_b_and_reset_do_not_reveal_student_a(self):
        other = Client()
        self.sign_in()
        self.sign_in(self.b, client=other)
        receipt = reset_student_credentials(actor=self.owner, classroom_id=self.room.pk, student_id=self.a.pk)
        self.assertEqual(self.client.get(self.detail_url).status_code, 302)
        self.assertEqual(other.get(self.list_url).status_code, 200)
        self.assertEqual(other.get(self.detail_url).status_code, 404)
        self.sign_in(password=receipt.password)
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(self.client.post(reverse("student-logout")).status_code, 302)
        self.sign_in(self.b)
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)
        self.assertNotContains(self.client.get(self.list_url), self.row.title)

    def test_pagination_never_introduces_other_student_rows(self):
        for n in range(21):
            lesson = create_lesson(actor=self.teacher, **self.lesson_data(title=f"Page lesson {n}"))
            self.assign(lesson_id=lesson.pk, expected_lesson_version=lesson.version)
        self.sign_in()
        first = self.client.get(self.list_url)
        second = self.client.get(self.list_url, {"page": 2, "student_id": self.b.pk})
        self.assertEqual(len(first.context["assignments"]), 20)
        self.assertEqual(len(second.context["assignments"]), 2)
        for response in (first, second):
            self.assertTrue(all(row.student_id == self.a.pk for row in response.context["assignments"]))

    def test_feature_disabled_and_unsupported_session_engine_close_routes(self):
        self.sign_in()
        for changes in ({"LMS_STUDENT_AUTH_ENABLED": False},
                        {"SESSION_ENGINE": "django.contrib.sessions.backends.signed_cookies"}):
            with self.settings(**changes):
                for url in (self.list_url, self.detail_url):
                    self.assertEqual(self.client.get(url).status_code, 404)

    def test_head_is_read_only_and_student_cannot_use_staff_mutation_routes(self):
        self.sign_in()
        for url in (self.list_url, self.detail_url):
            response = self.client.head(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"")
        url = reverse("lessons:assignment-cancel", args=[self.row.pk])
        self.assertEqual(self.client.post(url, {"confirm": "on", "expected_version": 1}).status_code, 403)
        self.row.refresh_from_db()
        self.assertIsNone(self.row.cancelled_at)
