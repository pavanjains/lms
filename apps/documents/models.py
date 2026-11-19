import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.lessons.models import Lesson

MAX_BYTES = 5 * 1024 * 1024


class LessonDocument(models.Model):
    lesson = models.ForeignKey("lessons.Lesson", on_delete=models.PROTECT, related_name="supporting_documents")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    original_name = models.CharField(max_length=200)
    size = models.PositiveIntegerField()
    checksum = models.CharField(max_length=64)
    content = models.BinaryField(editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=models.Q(size__gte=1, size__lte=MAX_BYTES), name="document_size_bounded",
        )]

    def clean(self):
        super().clean()
        self.title = (self.title or "").strip()
        payload = bytes(self.content or b"")
        if (not self.title or not 1 <= len(payload) <= MAX_BYTES or len(payload) != self.size
                or hashlib.sha256(payload).hexdigest() != self.checksum):
            raise ValidationError("Invalid document metadata or content.")
        lesson = Lesson.objects.filter(pk=self.lesson_id).first()
        uploader = get_user_model().objects.filter(pk=self.uploaded_by_id).first()
        if lesson and uploader and (uploader.organization_id != lesson.organization_id
                                    or uploader.role not in {"OWNER", "INSTRUCTOR"}):
            raise ValidationError("Uploader must be staff in the lesson organization.")
