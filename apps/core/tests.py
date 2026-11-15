from django.test import SimpleTestCase
from django.urls import reverse


class FoundationPageTests(SimpleTestCase):
    def test_home(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Robotics Learning Center")

    def test_liveness(self):
        response = self.client.get(reverse("liveness"))
        self.assertEqual(response.json(), {"status": "ok"})

    def test_liveness_rejects_post(self):
        self.assertEqual(self.client.post(reverse("liveness")).status_code, 405)
