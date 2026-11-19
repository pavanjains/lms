from django.template.loader import render_to_string
from django.test import Client, TestCase, override_settings
from django.urls import reverse


@override_settings(DEBUG=False, LMS_STAFF_AUTH_ENABLED=True, LMS_STUDENT_AUTH_ENABLED=True)
class StemboticBrandingTests(TestCase):
    def test_public_staff_student_and_error_pages(self):
        for url in (reverse("home"), reverse("two_factor:login"), reverse("student-login"), "/missing-stembotic-page/"):
            response = self.client.get(url)
            self.assertIn(b"Stembotic", response.content)
        for template in ("400.html", "403.html", "404.html", "500.html"):
            self.assertIn("Stembotic", render_to_string(template))

    def test_csrf_failure_is_branded_without_reason_details(self):
        response = Client(enforce_csrf_checks=True).post(reverse("student-login"), {})
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Stembotic", status_code=403)
        self.assertNotContains(response, "CSRF cookie not set", status_code=403)

    def test_health_json_unchanged(self):
        self.assertJSONEqual(self.client.get(reverse("liveness")).content, {"status": "ok"})
