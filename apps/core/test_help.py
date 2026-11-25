import time

from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.students import SEEN, STARTED, STUDENT_BACKEND
from apps.lessons import test_assignment_views as staff_foundation
from apps.lessons import test_assignments as foundation


@override_settings(DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class HelpManualTests(TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign
    login_staff = staff_foundation.InstructorAssignmentViewsTests.login_staff

    def login_student(self):
        self.client.force_login(self.a, backend=STUDENT_BACKEND)
        session = self.client.session
        session[STARTED] = session[SEEN] = time.time()
        session.save()

    def test_owner_sees_owner_manual_with_owner_links(self):
        self.login_staff(self.owner)
        response = self.client.get(reverse("staff-help"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owner manual")
        self.assertNotContains(response, "Instructor manual")
        self.assertContains(response, reverse("owner-accounts:instructors"))
        self.assertNotContains(response, "<script")

    def test_instructor_sees_instructor_manual_without_owner_links(self):
        self.login_staff()
        response = self.client.get(reverse("staff-help"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Instructor manual")
        self.assertNotContains(response, "Owner manual")
        self.assertNotContains(response, reverse("owner-accounts:instructors"))
        self.assertNotContains(response, "<script")

    def test_student_sees_student_manual_without_staff_urls(self):
        self.login_student()
        response = self.client.get(reverse("student-help"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student manual")
        self.assertNotContains(response, "/staff/")
        self.assertNotContains(response, "<script")
        self.assertIn("no-store", response["Cache-Control"])

    def test_help_marks_the_help_tab_current(self):
        self.login_staff()
        self.assertContains(
            self.client.get(reverse("staff-help")),
            '<a href="/staff/help/" aria-current="page">Help</a>', count=1,
        )
        self.login_student()
        self.assertContains(
            self.client.get(reverse("student-help")),
            '<a href="/students/help/" aria-current="page">Help</a>', count=1,
        )

    def test_anonymous_users_cannot_read_either_manual(self):
        staff = self.client.get(reverse("staff-help"))
        self.assertIn(staff.status_code, (302, 403))
        self.assertNotContains(staff, "manual", status_code=staff.status_code)
        student = self.client.get(reverse("student-help"))
        self.assertEqual(student.status_code, 302)
        self.assertEqual(student["Location"], reverse("student-login"))

    def test_roles_cannot_read_each_others_manuals(self):
        self.login_student()
        staff = self.client.get(reverse("staff-help"))
        self.assertIn(staff.status_code, (302, 403))
        self.assertNotContains(staff, "Student manual", status_code=staff.status_code)
        self.client.logout()
        self.login_staff()
        self.assertEqual(self.client.get(reverse("student-help")).status_code, 403)

    def test_help_tab_is_in_navigation_only_for_signed_in_users(self):
        self.assertNotContains(self.client.get(reverse("home")), "/help/")
        self.login_student()
        self.assertContains(self.client.get(reverse("home")), 'href="/students/help/"')
        self.assertNotContains(self.client.get(reverse("home")), "/staff/")
        self.client.logout()
        self.login_staff()
        self.assertContains(self.client.get(reverse("home")), 'href="/staff/help/"')

    def test_base_template_without_a_request_has_no_help_tab(self):
        self.assertNotIn("Help</a>", render_to_string("base.html"))

    def test_help_pages_reject_unsafe_methods(self):
        self.assertEqual(self.client.post(reverse("staff-help")).status_code, 405)
        self.assertEqual(self.client.post(reverse("student-help")).status_code, 405)
