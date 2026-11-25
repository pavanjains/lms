import time

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import StudentProfile
from apps.accounts.students import SEEN, STARTED, STUDENT_BACKEND
from apps.organizations.models import Organization

STAFF_BACKEND = "apps.accounts.backends.StaffEmailBackend"
CURRENT_HOME_LINK = '<a href="/" aria-current="page">Home</a>'


@override_settings(DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class HomeNavigationTests(TestCase):
    password = "Synthetic-Home-Nav-Only!48291"

    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic navigation center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="navowner", email="navowner@example.test", password=self.password,
            role="OWNER", organization=self.org,
        )
        self.student = User.objects.create_user(
            username="navstudent", password=self.password, role="STUDENT", organization=self.org,
        )
        StudentProfile.objects.create(user=self.student, grade="4")

    def test_home_offers_owner_instructor_and_student_sign_in(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        for label in ("Owner sign in", "Instructor sign in", "Student sign in"):
            self.assertContains(response, label)
        self.assertContains(response, 'href="/account/login/"', count=2)
        self.assertContains(response, 'href="/students/login/"', count=1)
        self.assertContains(response, "Robotics Learning Center")
        self.assertNotContains(response, "<script")

    @override_settings(LMS_STAFF_AUTH_ENABLED=False, LMS_STUDENT_AUTH_ENABLED=False)
    def test_disabled_sign_in_shows_note_not_a_dead_link(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/account/login/"')
        self.assertNotContains(response, 'href="/students/login/"')
        self.assertContains(response, "Staff sign-in is not enabled", count=2)
        self.assertContains(response, "Student sign-in is not enabled", count=1)

    def test_home_link_is_on_public_and_error_pages(self):
        for url in (reverse("home"), reverse("two_factor:login"), reverse("student-login"),
                    "/missing-home-navigation-page/"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(b'href="/"', response.content)

    def test_home_tab_is_marked_current_only_on_home(self):
        self.assertContains(self.client.get(reverse("home")), CURRENT_HOME_LINK, count=1)
        self.assertNotContains(self.client.get(reverse("student-login")), CURRENT_HOME_LINK)
        self.assertNotContains(self.client.get(reverse("two_factor:login")), CURRENT_HOME_LINK)

    def test_base_template_renders_without_a_request(self):
        html = render_to_string("base.html")
        self.assertIn('href="/"', html)
        self.assertNotIn(CURRENT_HOME_LINK, html)
        self.assertNotIn("My workspace", html)
        self.assertNotIn("<script", html)

    def test_signed_in_staff_sees_workspace_link_not_sign_in_cards(self):
        self.client.force_login(self.owner, backend=STAFF_BACKEND)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/staff/"')
        self.assertContains(response, "My workspace")
        self.assertNotContains(response, "Owner sign in")
        self.assertNotContains(response, "Student sign in")

    def test_signed_in_student_links_to_student_home_without_staff_urls(self):
        self.client.force_login(self.student, backend=STUDENT_BACKEND)
        session = self.client.session
        session[STARTED] = session[SEEN] = time.time()
        session.save()
        for url in (reverse("home"), reverse("student-home")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'href="/students/"')
                self.assertNotContains(response, "/staff/")
