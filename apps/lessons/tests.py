from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.lessons.models import Lesson
from apps.lessons.services import archive_lesson, create_lesson, update_lesson, visible_lessons
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class LessonLibraryTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.user("owner", "OWNER")
        self.teacher = self.user("teacher", "INSTRUCTOR")
        self.peer = self.user("peer", "INSTRUCTOR")
        self.foreign = self.user("foreign", "OWNER", self.other)

    def user(self, name, role, org=None):
        user = get_user_model().objects.create_user(username=name, email=name + "@example.test",
                                                    role=role, organization=org or self.org)
        user.is_verified = lambda: True
        return user

    def data(self, **changes):
        data = dict(title="Synthetic lesson", summary="Build and explore",
                    lego_url="https://education.lego.com/en-us/lessons/synthetic-not-verified/",
                    instructions="Follow instructor guidance.", kit="ESSENTIAL", min_grade=1, max_grade=4)
        data.update(changes)
        return data

    def create(self, actor=None, **changes):
        return create_lesson(actor=actor or self.teacher, **self.data(**changes))

    def login(self, user=None, client=None):
        user, client = user or self.teacher, client or self.client
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def test_create_inherits_org_and_creator(self):
        lesson = self.create()
        self.assertEqual(lesson.organization_id, self.org.pk)
        self.assertEqual(lesson.created_by_id, self.teacher.pk)
        self.assertEqual(lesson.version, 1)
        self.assertTrue(visible_lessons(self.peer).filter(pk=lesson.pk).exists())
        self.assertFalse(visible_lessons(self.foreign).filter(pk=lesson.pk).exists())

    def test_grade_four_accepts_either_kit(self):
        for kit in ("ESSENTIAL", "PRIME"):
            self.assertEqual(self.create(kit=kit, min_grade=4, max_grade=4).kit, kit)

    def test_invalid_ranges_and_kits_rejected(self):
        for changes in (dict(max_grade=5), dict(kit="PRIME", min_grade=3),
                        dict(min_grade=5, max_grade=4), dict(min_grade=-2), dict(kit="OTHER")):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.create(**changes)
        self.assertFalse(Lesson.objects.exists())

    def test_database_enforces_kit_range(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Lesson.objects.create(organization=self.org, created_by=self.teacher, **self.data(max_grade=5))

    def test_non_lego_non_https_credentials_and_port_rejected(self):
        for url in ("http://education.lego.com/lesson", "https://attacker.example/",
                    "https://education.lego.com.attacker.example/", "https://user:pass@education.lego.com/",
                    "https://education.lego.com:8443/", "javascript:alert(1)"):
            with self.subTest(url=url), self.assertRaises(ValidationError):
                self.create(lego_url=url)

    def test_only_creator_or_owner_can_edit_and_version_prevents_stale_save(self):
        lesson = self.create()
        with self.assertRaises(PermissionDenied):
            update_lesson(actor=self.peer, lesson_id=lesson.pk, expected_version=1, **self.data())
        saved = update_lesson(actor=self.owner, lesson_id=lesson.pk, expected_version=1,
                              **self.data(title="Updated"))
        self.assertEqual(saved.version, 2)
        with self.assertRaises(ValidationError):
            update_lesson(actor=self.teacher, lesson_id=lesson.pk, expected_version=1, **self.data())
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, "Updated")

    def test_archive_retained_and_scoped(self):
        lesson = self.create()
        archive_lesson(actor=self.teacher, lesson_id=lesson.pk, expected_version=1)
        self.assertTrue(Lesson.objects.filter(pk=lesson.pk).exists())
        self.assertFalse(visible_lessons(self.peer).filter(pk=lesson.pk).exists())
        self.assertTrue(visible_lessons(self.owner).filter(pk=lesson.pk).exists())
        with self.assertRaises(ValidationError):
            update_lesson(actor=self.teacher, lesson_id=lesson.pk, expected_version=2, **self.data())

    def test_fresh_actor_and_no_privilege_injection(self):
        with self.assertRaises(ValidationError):
            self.create(organization=self.other)
        get_user_model().objects.filter(pk=self.teacher.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.create()
        self.owner.is_verified = lambda: False
        with self.assertRaises(PermissionDenied):
            self.create(self.owner)

    def test_list_filters_and_external_link_escaping(self):
        essential = self.create(title="Essential Four", min_grade=4, max_grade=4, instructions="<script>bad()</script>")
        self.create(title="Prime Four", kit="PRIME", min_grade=4, max_grade=4)
        self.login()
        response = self.client.get(reverse("lessons:list"), {"grade": "4"})
        self.assertContains(response, "Essential Four")
        self.assertContains(response, "Prime Four")
        response = self.client.get(reverse("lessons:list"), {"kit": "PRIME", "q": "Four"})
        self.assertNotContains(response, "Essential Four")
        response = self.client.get(reverse("lessons:detail", args=[essential.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["Referrer-Policy"], "same-origin")

    def test_get_and_unconfirmed_post_do_not_create(self):
        self.login()
        url = reverse("lessons:create")
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url, self.data()).status_code, 400)
        self.assertFalse(Lesson.objects.exists())
        self.assertEqual(self.client.post(url, {**self.data(), "confirm": "on"}).status_code, 302)

    def test_foreign_and_peer_mutation_blocked(self):
        lesson = self.create()
        self.login(self.peer)
        self.assertEqual(self.client.get(reverse("lessons:edit", args=[lesson.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse("lessons:archive", args=[lesson.pk]),
                                          {"confirm": "on", "expected_version": 1}).status_code, 403)
        foreign = self.create(self.foreign)
        self.assertEqual(self.client.get(reverse("lessons:detail", args=[foreign.pk])).status_code, 404)

    def test_csrf_tokens_origins_and_methods(self):
        client = Client(enforce_csrf_checks=True)
        self.login(client=client)
        url = reverse("lessons:create")
        self.assertEqual(client.post(url, self.data()).status_code, 403)
        client.get(url)
        data = {**self.data(), "confirm": "on", "csrfmiddlewaretoken": client.cookies["csrftoken"].value}
        for origin in ("null", "https://attacker.example"):
            self.assertEqual(client.post(url, data, HTTP_ORIGIN=origin).status_code, 403)
        self.assertEqual(client.post(url, data, HTTP_ORIGIN="http://testserver").status_code, 302)
        self.assertEqual(client.put(url, {}).status_code, 403)

    def test_anonymous_unverified_and_disabled(self):
        self.assertEqual(self.client.get(reverse("lessons:list")).status_code, 302)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("lessons:list")).status_code, 302)
        with self.settings(LMS_STAFF_AUTH_ENABLED=False):
            self.assertEqual(self.client.get(reverse("lessons:list")).status_code, 404)

    def test_student_cannot_read_or_create(self):
        student = get_user_model().objects.create_user(username="learner", role="STUDENT", organization=self.org)
        student.is_verified = lambda: True
        with self.assertRaises(PermissionDenied):
            visible_lessons(student)
        with self.assertRaises(PermissionDenied):
            self.create(student)
