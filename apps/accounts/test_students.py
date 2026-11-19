import time

from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, authenticate, get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import StudentProfile
from apps.accounts.students import SEEN, STARTED, STUDENT_BACKEND
from apps.classrooms.credential_services import reset_student_credentials
from apps.classrooms.models import ClassEnrollment, Classroom
from apps.organizations.models import Organization


@override_settings(LMS_STUDENT_AUTH_ENABLED=True, LMS_STAFF_AUTH_ENABLED=True)
class StudentSignInTests(TestCase):
    password = "Synthetic-Student-Password!7429"

    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.user("owner", "OWNER")
        self.a = self.user("student-a", "STUDENT")
        self.b = self.user("student-b", "STUDENT", self.other)
        self.room = Classroom.objects.create(organization=self.org, name="A private class", created_by=self.owner)
        self.foreign = Classroom.objects.create(organization=self.other, name="B private class", created_by=self.b)
        ClassEnrollment.objects.create(classroom=self.room, student=self.a)
        ClassEnrollment.objects.create(classroom=self.foreign, student=self.b)
        self.url = reverse("student-login")

    def user(self, username, role, org=None):
        user = get_user_model().objects.create_user(
            username=username, email=username + "@example.test" if role != "STUDENT" else "",
            role=role, organization=org or self.org, display_name=username, password=self.password,
        )
        if role == "STUDENT":
            StudentProfile.objects.create(user=user, grade="4")
        return user

    def sign_in(self, client=None, user=None, password=None, **extra):
        return (client or self.client).post(self.url, {
            "student_username": (user or self.a).username,
            "password": password or self.password, **extra,
        })

    def test_login_flushes_anonymous_context_and_rotates_key(self):
        session = self.client.session
        session["previous_student_data"] = "must disappear"
        session.save()
        old_key = session.session_key
        self.assertRedirects(self.sign_in(), reverse("student-home"), fetch_redirect_response=False)
        self.assertNotEqual(self.client.session.session_key, old_key)
        self.assertNotIn("previous_student_data", self.client.session)
        self.assertEqual(self.client.session[BACKEND_SESSION_KEY], STUDENT_BACKEND)
        self.assertNotIn(self.password, str(dict(self.client.session)))

    def test_self_only_dashboard_ignores_student_id_parameters(self):
        self.sign_in()
        response = self.client.get(reverse("student-home"), {"student_id": self.b.pk})
        self.assertContains(response, self.a.display_name)
        self.assertContains(response, "A private class")
        self.assertNotContains(response, self.b.display_name)
        self.assertNotContains(response, "B private class")
        self.assertNotContains(response, self.password)
        self.assertIn("no-store", response["Cache-Control"])

    def test_generic_failure_staff_credentials_and_wrong_entrypoint(self):
        for user, password in ((self.a, "incorrect"), (self.owner, self.password)):
            self.assertEqual(self.sign_in(user=user, password=password).status_code, 400)
        response = self.client.post(self.url, {"student_username": "missing", "password": self.password})
        self.assertContains(response, "Unable to sign in", status_code=400)
        self.assertIsNone(authenticate(username=self.a.username, password=self.password))
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_account_switch_requires_logout_and_wrong_staff_route_preserves_session(self):
        self.sign_in()
        key = self.client.session.session_key
        self.assertEqual(self.sign_in(user=self.b).status_code, 409)
        self.assertEqual(self.client.get(reverse("staff-home")).status_code, 403)
        self.assertEqual(self.client.get(reverse("two_factor:login")).status_code, 403)
        self.assertEqual(self.client.session.session_key, key)
        self.assertEqual(str(self.client.session[SESSION_KEY]), str(self.a.pk))

    def test_staff_cannot_use_student_routes_or_be_silently_replaced(self):
        self.client.force_login(self.owner, backend="apps.accounts.backends.StaffEmailBackend")
        key = self.client.session.session_key
        self.assertEqual(self.client.get(self.url).status_code, 409)
        self.assertEqual(self.sign_in().status_code, 409)
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 403)
        self.assertEqual(self.client.post(reverse("student-logout")).status_code, 403)
        self.assertEqual(self.client.session.session_key, key)

    def test_post_logout_and_next_student(self):
        self.sign_in()
        self.assertEqual(self.client.get(reverse("student-logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("student-logout")).status_code, 302)
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)
        self.sign_in(user=self.b)
        response = self.client.get(reverse("student-home"))
        self.assertContains(response, "B private class")
        self.assertNotContains(response, "A private class")

    def test_idle_and_absolute_expiry(self):
        for absolute in (False, True):
            with self.subTest(absolute=absolute):
                self.sign_in()
                session = self.client.session
                now = time.time()
                session[STARTED] = now - (14401 if absolute else 1000)
                session[SEEN] = now - (1 if absolute else 901)
                session.save()
                self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)
                self.assertNotIn(SESSION_KEY, self.client.session)

    def test_missing_or_invalid_session_timestamps_denied(self):
        self.client.force_login(self.a, backend=STUDENT_BACKEND)
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)
        self.sign_in()
        session = self.client.session
        session[SEEN] = "forged"
        session.save()
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)

    def test_inactive_account_org_and_missing_profile_denied(self):
        for model, query, update in (
            (get_user_model(), {"pk": self.a.pk}, {"is_active": False}),
            (Organization, {"pk": self.org.pk}, {"is_active": False}),
        ):
            self.sign_in()
            model.objects.filter(**query).update(**update)
            self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)
            self.assertEqual(self.sign_in().status_code, 400)
            model.objects.filter(**query).update(is_active=True)
        StudentProfile.objects.filter(user=self.a).delete()
        self.assertEqual(self.sign_in().status_code, 400)

    def test_role_change_does_not_promote_student_session(self):
        self.sign_in()
        get_user_model().objects.filter(pk=self.a.pk).update(role="INSTRUCTOR", email="changed@example.test")
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_enrollment_removal_and_archive_hide_classes(self):
        self.sign_in()
        ClassEnrollment.objects.filter(student=self.a).update(is_active=False)
        self.assertContains(self.client.get(reverse("student-home")), "No active classes")
        ClassEnrollment.objects.filter(student=self.a).update(is_active=True)
        Classroom.objects.filter(pk=self.room.pk).update(is_active=False)
        self.assertContains(self.client.get(reverse("student-home")), "No active classes")

    def test_reset_invalidates_target_session_not_other_student(self):
        other = Client()
        self.sign_in()
        self.sign_in(other, self.b)
        self.owner.is_verified = lambda: True
        credentials = reset_student_credentials(actor=self.owner, classroom_id=self.room.pk, student_id=self.a.pk)
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)
        self.assertEqual(other.get(reverse("student-home")).status_code, 200)
        self.assertEqual(self.sign_in().status_code, 400)
        self.assertEqual(self.sign_in(password=credentials.password).status_code, 302)

    def test_password_hash_change_also_invalidates_without_row_deletion(self):
        self.sign_in()
        self.a.set_password("Synthetic-New-Password!8381")
        self.a.save(update_fields=["password"])
        self.assertEqual(self.client.get(reverse("student-home")).status_code, 302)

    def test_csrf_login_logout_and_fixed_redirect(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(self.sign_in(client).status_code, 403)
        self.assertEqual(client.get(self.url).status_code, 200)
        token = client.cookies["csrftoken"].value
        self.assertEqual(self.sign_in(client, csrfmiddlewaretoken=token, next="https://attacker.example").url, reverse("student-home"))
        self.assertEqual(client.post(reverse("student-logout")).status_code, 403)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(reverse("student-logout"), {"csrfmiddlewaretoken": token}).status_code, 302)

    @override_settings(LMS_STUDENT_AUTH_ENABLED=False)
    def test_disabled_student_flag(self):
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertIsNone(authenticate(student_username=self.a.username, password=self.password))

    @override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
    def test_unsupported_session_backend_closed(self):
        self.assertEqual(self.client.get(self.url).status_code, 404)
