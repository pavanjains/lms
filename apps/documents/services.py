import hashlib

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Sum
from django.http import Http404
from django.utils import timezone

from apps.classrooms.policies import current_staff
from apps.classrooms.services import _lock_actor
from apps.documents.models import MAX_BYTES, LessonDocument
from apps.lessons.services import can_manage, locked_lesson, visible_lessons

MAX_ACTIVE_DOCS = 20
MAX_ORG_BYTES = 100 * 1024 * 1024


def enabled():
    if not getattr(settings, "LMS_LESSON_DOCUMENTS_ENABLED", False):
        raise Http404


def upload_document(*, actor, lesson_id, expected_version, title, upload):
    enabled()
    user = current_staff(actor)
    lesson = visible_lessons(actor).filter(pk=lesson_id).first()
    if lesson is None or not can_manage(user, lesson):
        raise PermissionDenied
    name = getattr(upload, "name", "").replace("\\", "/").rsplit("/", 1)[-1]
    if (not name.lower().endswith(".pdf") or len(name) > 200
            or any(ord(char) < 32 for char in name)
            or not getattr(upload, "size", 0) or upload.size > MAX_BYTES):
        raise ValidationError("Upload a nonempty PDF no larger than 5 MiB.")
    buffer = bytearray()
    for chunk in upload.chunks():
        if len(buffer) + len(chunk) > MAX_BYTES:
            raise ValidationError("PDF exceeds the upload limit.")
        buffer.extend(chunk)
    payload = bytes(buffer)
    if not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-1024:]:
        raise ValidationError("PDF signature or end marker missing.")
    with transaction.atomic():
        user = _lock_actor(actor)
        lesson = locked_lesson(user, lesson_id, expected_version)
        if not lesson.is_active:
            raise ValidationError("Cannot upload to an archived lesson.")
        if LessonDocument.objects.filter(lesson=lesson, is_active=True).count() >= MAX_ACTIVE_DOCS:
            raise ValidationError("Active document limit reached for this lesson.")
        total = LessonDocument.objects.filter(lesson__organization_id=user.organization_id).aggregate(
            total=Sum("size"),
        )["total"] or 0
        if total + len(payload) > MAX_ORG_BYTES:
            raise ValidationError("Organization document quota reached, including archived content.")
        document = LessonDocument(lesson=lesson, uploaded_by=user, title=title, original_name=name,
                                  size=len(payload), checksum=hashlib.sha256(payload).hexdigest(), content=payload)
        document.full_clean()
        document.save()
        lesson.version += 1
        lesson.save(update_fields=["version", "updated_at"])
        return document


@transaction.atomic
def archive_document(*, actor, lesson_id, document_id, expected_version):
    enabled()
    user = _lock_actor(actor)
    lesson = locked_lesson(user, lesson_id, expected_version)
    if not lesson.is_active:
        raise ValidationError("Cannot change documents on an archived lesson.")
    document = LessonDocument.objects.select_for_update().defer("content").filter(
        pk=document_id, lesson=lesson, is_active=True,
    ).first()
    if document is None:
        raise PermissionDenied
    document.is_active = False
    document.archived_at = timezone.now()
    document.save(update_fields=["is_active", "archived_at"])
    lesson.version += 1
    lesson.save(update_fields=["version", "updated_at"])
    return document
