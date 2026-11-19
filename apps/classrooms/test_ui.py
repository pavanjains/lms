from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class ClassroomUITests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.user("owner", "OWNER")
        self.teacher = self.user("teacher", "INSTRUCTOR")
        self.student = self.user("student", "STUDENT")
        self.hidden = self.user("hidden-student", "STUDENT")
        self.foreign = self.user("foreign-instructor", "INSTRUCTOR", self.other)
        self.room = Classroom.objects.create(organization=self.org, name="Robotics", created_by=self.owner)
        self.extra = Classroom.objects.create(organization=self.org, name="Other class", created_by=self.owner)
        ClassInstructor.objects.create(classroom=self.room, instructor=self.teacher)
        ClassEnrollment.objects.create(classroom=self.room, student=self.student)
        self.login(self.owner)

    def user(self, name, role, org=None):
        user = get_user_model().objects.create_user(
            username=name, email=name + "@example.test" if role != "STUDENT" else "",
            organization=org or self.org, role=role,
        )
        if role == "STUDENT":
            StudentProfile.objects.create(user=user, grade="4")
        return user

    def login(self, user, client=None):
        client = client or self.client
        device, _ = TOTPDevice.objects.get_or_create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def action(self, operation, room=None):
        return reverse("classrooms:action", args=[(room or self.room).pk, operation])

    def test_list_detail_and_private_headers(self):
        response = self.client.get(reverse("classrooms:list"))
        self.assertContains(response, "Robotics")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        response = self.client.get(reverse("classrooms:detail", args=[self.room.pk]))
        self.assertContains(response, "student")
        self.assertNotContains(response, self.student.password)

    def test_create_requires_confirmation_and_ignores_org_injection(self):
        url = reverse("classrooms:create")
        self.assertEqual(self.client.post(url, {"name": "New"}).status_code, 400)
        response = self.client.post(url, {"name": "New", "confirm": "on",
                                          "organization": str(self.other.pk)})
        room = Classroom.objects.get(name="New")
        self.assertEqual(room.organization_id, self.org.pk)
        self.assertRedirects(response, reverse("classrooms:detail", args=[room.pk]),
                             fetch_redirect_response=False)
        self.assertEqual(self.client.post(url, {"name": "NEW", "confirm": "on"}).status_code, 400)

    def test_get_actions_are_read_only_and_confirmation_required(self):
        for operation in ("archive", "assign-instructor", "remove-instructor",
                          "enroll-student", "end-enrollment"):
            with self.subTest(operation=operation):
                url = self.action(operation)
                self.assertEqual(self.client.get(url).status_code, 200)
                self.assertEqual(self.client.post(url, {}).status_code, 400)
        self.room.refresh_from_db()
        self.assertTrue(self.room.is_active)
        self.assertEqual(ClassEnrollment.objects.count(), 1)

    def test_owner_membership_and_enrollment_changes(self):
        for operation, target in (("remove-instructor", self.teacher),
                                  ("assign-instructor", self.teacher),
                                  ("enroll-student", self.hidden),
                                  ("end-enrollment", self.hidden)):
            response = self.client.post(self.action(operation), {"target": target.pk, "confirm": "on"})
            self.assertEqual(response.status_code, 302)
        self.assertFalse(ClassEnrollment.objects.get(student=self.hidden).is_active)

    def test_foreign_choice_and_class_are_hidden(self):
        url = self.action("assign-instructor")
        self.assertNotContains(self.client.get(url), self.foreign.username)
        self.assertEqual(self.client.post(url, {"target": self.foreign.pk, "confirm": "on"}).status_code, 400)
        foreign_room = Classroom.objects.create(organization=self.other, name="Foreign", created_by=self.foreign)
        self.assertEqual(self.client.get(reverse("classrooms:detail", args=[foreign_room.pk])).status_code, 404)

    def test_instructor_scope_and_forged_actions(self):
        self.login(self.teacher)
        self.assertNotContains(self.client.get(reverse("classrooms:list")), "Other class")
        self.assertEqual(self.client.get(reverse("classrooms:detail", args=[self.extra.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("classrooms:create")).status_code, 403)
        for operation in ("archive", "assign-instructor", "remove-instructor"):
            self.assertEqual(self.client.post(self.action(operation), {"confirm": "on"}).status_code, 403)
        url = self.action("enroll-student")
        self.assertNotContains(self.client.get(url), self.hidden.username)
        self.assertEqual(self.client.post(url, {"target": self.hidden.pk, "confirm": "on"}).status_code, 400)

    def test_instructor_can_enroll_visible_student_in_second_assigned_class(self):
        ClassInstructor.objects.create(classroom=self.extra, instructor=self.teacher)
        self.login(self.teacher)
        response = self.client.post(self.action("enroll-student", self.extra),
                                    {"target": self.student.pk, "confirm": "on"})
        self.assertEqual(response.status_code, 302)

    def test_archive_and_removed_membership_block_access(self):
        self.assertEqual(self.client.post(self.action("archive"), {"confirm": "on"}).status_code, 302)
        self.assertTrue(ClassEnrollment.objects.filter(classroom=self.room).exists())
        response = self.client.get(reverse("classrooms:detail", args=[self.room.pk]))
        self.assertContains(response, "This class is archived")
        self.login(self.teacher)
        self.assertEqual(self.client.get(reverse("classrooms:detail", args=[self.room.pk])).status_code, 404)

    def test_removed_membership_denies_next_request(self):
        self.login(self.teacher)
        ClassInstructor.objects.filter(classroom=self.room, instructor=self.teacher).update(is_active=False)
        self.assertEqual(self.client.get(reverse("classrooms:detail", args=[self.room.pk])).status_code, 404)

    def test_csrf_origin_and_token_checks(self):
        client = Client(enforce_csrf_checks=True)
        self.login(self.owner, client)
        url = reverse("classrooms:create")
        self.assertEqual(client.post(url, {"name": "Denied", "confirm": "on"}).status_code, 403)
        self.assertEqual(client.get(url).status_code, 200)
        data = {"name": "CSRF class", "confirm": "on",
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value}
        self.assertEqual(client.post(url, data, HTTP_ORIGIN="null").status_code, 403)
        self.assertEqual(client.post(url, data, HTTP_ORIGIN="https://attacker.example").status_code, 403)
        self.assertEqual(client.post(url, data, HTTP_ORIGIN="http://testserver").status_code, 302)

    def test_mfa_and_anonymous_redirect_to_login(self):
        for client in (Client(), Client()):
            client.force_login(self.owner)
            self.assertEqual(client.get(reverse("classrooms:list")).status_code, 302)
        self.assertEqual(Client().get(reverse("classrooms:list")).status_code, 302)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_disabled_gate(self):
        self.assertEqual(self.client.get(reverse("classrooms:list")).status_code, 404)

    def test_unknown_action_and_unsupported_method(self):
        self.assertEqual(self.client.get(self.action("unknown")).status_code, 404)
        self.assertEqual(self.client.put(reverse("classrooms:create")).status_code, 405)
