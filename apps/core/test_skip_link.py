import time
from html.parser import HTMLParser

from django.template.loader import render_to_string
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.students import SEEN, STARTED, STUDENT_BACKEND
from apps.lessons import test_assignment_views as staff_foundation
from apps.lessons import test_assignments as foundation


class BodyElements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.elements = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        elif self.in_body:
            self.elements.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False


class SkipLinkAssertions:
    def assert_skip_link(self, html):
        parser = BodyElements()
        parser.feed(html)
        elements = parser.elements
        links = [(i, attrs) for i, (tag, attrs) in enumerate(elements)
                 if tag == "a" and attrs.get("href") == "#main"]
        self.assertEqual(len(links), 1)
        index, link = links[0]
        self.assertIn("skip-link", link.get("class", "").split())
        targets = [(i, tag, attrs) for i, (tag, attrs) in enumerate(elements)
                   if attrs.get("id") == "main"]
        self.assertEqual(len(targets), 1)
        target_index, tag, target = targets[0]
        self.assertEqual(tag, "main")
        self.assertEqual(target.get("tabindex"), "-1")
        self.assertLess(index, target_index)
        self.assertEqual(sum(tag == "main" for tag, attrs in elements), 1)
        headers = [i for i, (tag, attrs) in enumerate(elements) if tag == "header"]
        self.assertTrue(headers)
        self.assertLess(index, headers[0])
        focusable = [(tag, attrs) for tag, attrs in elements
                     if ((tag == "a" and "href" in attrs)
                         or tag in {"button", "input", "select", "textarea"})
                     and "disabled" not in attrs and attrs.get("type") != "hidden"
                     and attrs.get("tabindex", "0") != "-1"]
        self.assertTrue(focusable)
        self.assertEqual(focusable[0], ("a", link))
        self.assertNotIn("onclick", link)
        self.assertNotIn("autofocus", target)


@override_settings(DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class SkipLinkPublicTests(SkipLinkAssertions, TestCase):
    def test_public_entry_pages_have_first_skip_link_and_focusable_unique_main(self):
        for url in (reverse("home"), reverse("two_factor:login"), reverse("student-login")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assert_skip_link(response.content.decode())

    def test_error_templates_inherit_skip_link_target(self):
        for template in ("400.html", "403.html", "404.html", "500.html"):
            with self.subTest(template=template):
                self.assert_skip_link(render_to_string(template))
        response = self.client.get("/missing-skip-link-test-page/")
        self.assertEqual(response.status_code, 404)
        self.assert_skip_link(response.content.decode())

    def test_csrf_error_keeps_shared_skip_link(self):
        response = Client(enforce_csrf_checks=True).post(reverse("student-login"), {})
        self.assertEqual(response.status_code, 403)
        self.assert_skip_link(response.content.decode())

    def test_focus_styles_and_native_fragment_contract(self):
        html = render_to_string("base.html")
        self.assert_skip_link(html)
        self.assertIn(".skip-link:focus, main:focus", html)
        self.assertIn("outline: 3px solid #005fcc", html)
        self.assertIn("outline-offset: 0.25rem", html)
        self.assertNotIn("<script", html)


@override_settings(DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class SkipLinkAuthenticatedTests(SkipLinkAssertions, TestCase):
    setUp = foundation.AssignmentFoundationTests.setUp
    make_user = foundation.AssignmentFoundationTests.make_user
    lesson_data = foundation.AssignmentFoundationTests.lesson_data
    assign = foundation.AssignmentFoundationTests.assign
    login_staff = staff_foundation.InstructorAssignmentViewsTests.login_staff

    def test_staff_workspace_roster_and_assignment_pages_inherit_target(self):
        self.login_staff()
        for url in (reverse("staff-home"), reverse("classrooms:detail", args=[self.room.pk]),
                    reverse("lessons:list"), reverse("lessons:assignment-create", args=[self.room.pk])):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assert_skip_link(response.content.decode())

    def test_student_home_and_own_assignment_pages_inherit_target(self):
        row = self.assign()[0]
        self.client.force_login(self.a, backend=STUDENT_BACKEND)
        session = self.client.session
        session[STARTED] = session[SEEN] = time.time()
        session.save()
        for url in (reverse("student-home"), reverse("student-assignment-list"),
                    reverse("student-assignment-detail", args=[row.pk])):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assert_skip_link(response.content.decode())
