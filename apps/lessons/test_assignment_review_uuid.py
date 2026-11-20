import json
from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, Classroom
from apps.lessons.assignment_views import REVIEW_KEY, REVIEW_SALT
from apps.lessons.models import LessonAssignment
from apps.lessons.services import create_lesson
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class AssignmentReviewUUIDTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic UUID review center")
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="uuid-owner", email="uuid-owner@example.test",
            role="OWNER", organization=self.org,
        )
        self.owner.is_verified = lambda: True
        self.student = User.objects.create_user(
            username="uuid-student", role="STUDENT", organization=self.org,
        )
        StudentProfile.objects.create(user=self.student, grade="4")
        self.room = Classroom.objects.create(
            organization=self.org, created_by=self.owner, name="UUID builders",
        )
        ClassEnrollment.objects.create(classroom=self.room, student=self.student)
        self.lesson = create_lesson(
            actor=self.owner, title="Synthetic UUID lesson", summary="Review serialization",
            lego_url="https://education.lego.com/en-us/lessons/synthetic-not-verified/",
            instructions="Build with your instructor.", kit="ESSENTIAL", min_grade=4, max_grade=4,
        )
        device = TOTPDevice.objects.create(user=self.owner, name="default", confirmed=True)
        self.client.force_login(self.owner)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        self.url = reverse("lessons:assignment-create", args=[self.room.pk])

    def review_token(self):
        response = self.client.post(self.url, {
            "action": "review", "lesson": self.lesson.pk, "students": [self.student.pk],
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LessonAssignment.objects.exists())
        return response.context["form"].initial["token"]

    def test_uuid_organization_review_and_confirmation_round_trip(self):
        self.assertIsInstance(self.org.pk, UUID)
        token = self.review_token()
        data = signing.loads(token, salt=REVIEW_SALT)
        self.assertIsInstance(data["org"], str)
        self.assertEqual(data["org"], str(self.org.pk))
        self.assertEqual(json.loads(json.dumps(data)), data)
        response = self.client.post(self.url, {
            "action": "confirm", "token": token, "confirm": "on",
        })
        self.assertEqual(response.status_code, 302)
        row = LessonAssignment.objects.get()
        self.assertEqual(row.organization_id, self.org.pk)
        self.assertEqual(row.student_id, self.student.pk)
        self.assertEqual(row.lesson_id, self.lesson.pk)
        self.assertNotIn(REVIEW_KEY, self.client.session)

    def test_validly_signed_different_organization_still_denied(self):
        data = signing.loads(self.review_token(), salt=REVIEW_SALT)
        different_org = uuid4()
        self.assertNotEqual(different_org, self.org.pk)
        data["org"] = str(different_org)
        token = signing.dumps(data, salt=REVIEW_SALT)
        session = self.client.session
        session[REVIEW_KEY] = token
        session.save()
        response = self.client.post(self.url, {
            "action": "confirm", "token": token, "confirm": "on",
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(LessonAssignment.objects.exists())
