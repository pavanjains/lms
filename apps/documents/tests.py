from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.documents.models import LessonDocument
from apps.documents.services import archive_document, upload_document
from apps.lessons.models import Lesson
from apps.organizations.models import Organization

PDF = b"%PDF-1.4\nSynthetic signature-only fixture\n%%EOF\n"


@override_settings(LMS_STAFF_AUTH_ENABLED=True, LMS_LESSON_DOCUMENTS_ENABLED=True)
class LessonDocumentTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.user("owner", "OWNER")
        self.teacher = self.user("teacher", "INSTRUCTOR")
        self.peer = self.user("peer", "INSTRUCTOR")
        self.foreign = self.user("foreign", "OWNER", self.other)
        self.lesson = Lesson.objects.create(
            organization=self.org, created_by=self.teacher, title="Synthetic", summary="",
            lego_url="https://education.lego.com/en-us/lessons/synthetic-not-verified/",
            instructions="Synthetic instructions", kit="ESSENTIAL", min_grade=1, max_grade=4,
        )

    def user(self, name, role, org=None):
        user = get_user_model().objects.create_user(username=name, email=name + "@example.test",
                                                    organization=org or self.org, role=role)
        user.is_verified = lambda: True
        return user

    def file(self, name="guide.pdf", content=PDF):
        return SimpleUploadedFile(name, content, content_type="application/pdf")

    def upload(self, actor=None, **changes):
        self.lesson.refresh_from_db()
        data = dict(actor=actor or self.teacher, lesson_id=self.lesson.pk,
                    expected_version=self.lesson.version, title="Guide", upload=self.file())
        data.update(changes)
        return upload_document(**data)

    def login(self, user=None, client=None):
        user, client = user or self.teacher, client or self.client
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        client.force_login(user)
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def test_atomic_content_and_version(self):
        document = self.upload()
        self.assertEqual(bytes(document.content), PDF)
        self.assertEqual(document.size, len(PDF))
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.version, 2)

    def test_pdf_extension_signature_and_size(self):
        for file in (self.file("bad.html"), self.file(content=b"<html>not pdf</html>"),
                     self.file(content=b"%PDF-no-end"), self.file(content=b"x" * (5242880 + 1))):
            with self.subTest(name=file.name), self.assertRaises(ValidationError):
                self.upload(upload=file)
        self.assertFalse(LessonDocument.objects.exists())

    def test_creator_owner_and_scope(self):
        with self.assertRaises(PermissionDenied):
            self.upload(self.peer)
        with self.assertRaises(PermissionDenied):
            self.upload(self.foreign)
        self.upload(self.owner)

    def test_quota_and_stale_version(self):
        self.upload()
        with self.assertRaises(ValidationError):
            self.upload(expected_version=1)
        with patch("apps.documents.services.MAX_ACTIVE_DOCS", 1):
            with self.assertRaises(ValidationError):
                self.upload()
        with patch("apps.documents.services.MAX_ORG_BYTES", len(PDF)):
            with self.assertRaises(ValidationError):
                self.upload()
        self.assertEqual(LessonDocument.objects.count(), 1)

    def test_save_failure_rolls_back_document_and_parent_version(self):
        with patch("apps.documents.services.LessonDocument.save", side_effect=RuntimeError("synthetic")):
            with self.assertRaises(RuntimeError):
                self.upload()
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.version, 1)
        self.assertFalse(LessonDocument.objects.exists())

    def test_archive_removes_download_but_retains_content(self):
        document = self.upload()
        archive_document(actor=self.teacher, lesson_id=self.lesson.pk, document_id=document.pk, expected_version=2)
        document.refresh_from_db()
        self.assertFalse(document.is_active)
        self.assertEqual(bytes(document.content), PDF)
        self.login()
        url = reverse("lessons:download-document", args=[self.lesson.pk, document.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_authorized_download_forces_attachment(self):
        document = self.upload()
        self.login(self.peer)
        response = self.client.get(reverse("lessons:download-document", args=[self.lesson.pk, document.pk]))
        self.assertEqual(b"".join(response.streaming_content), PDF)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(response["Content-Type"], "application/octet-stream")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertIn("no-store", response["Cache-Control"])

    def test_foreign_hidden_and_peer_upload_denied(self):
        document = self.upload()
        self.login(self.foreign)
        self.assertEqual(self.client.get(reverse("lessons:download-document", args=[self.lesson.pk, document.pk])).status_code, 404)
        client = Client()
        self.login(self.peer, client)
        self.assertEqual(client.get(reverse("lessons:upload-document", args=[self.lesson.pk])).status_code, 403)

    def test_integrity_failure_does_not_serve_bytes(self):
        document = self.upload()
        LessonDocument.objects.filter(pk=document.pk).update(content=b"corrupt")
        self.login()
        self.assertEqual(self.client.get(reverse("lessons:download-document", args=[self.lesson.pk, document.pk])).status_code, 404)

    def test_upload_form_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.login(client=client)
        url = reverse("lessons:upload-document", args=[self.lesson.pk])
        self.assertEqual(client.get(url).status_code, 200)
        self.assertFalse(LessonDocument.objects.exists())
        self.assertEqual(client.post(url, {}).status_code, 403)
        token = client.cookies["csrftoken"].value
        data = dict(title="Guide", file=self.file(), confirm="on", expected_version=1, csrfmiddlewaretoken=token)
        self.assertEqual(client.post(url, data, HTTP_ORIGIN="http://testserver").status_code, 302)

    @override_settings(LMS_LESSON_DOCUMENTS_ENABLED=False)
    def test_gate_closed(self):
        self.login()
        self.assertEqual(self.client.get(reverse("lessons:documents", args=[self.lesson.pk])).status_code, 404)
        with self.assertRaises(Exception) as raised:
            self.upload()
        self.assertEqual(type(raised.exception).__name__, "Http404")
