from django.conf import settings
from django.db import models
from django.db.models import Q


class AuditEventType(models.TextChoices):
    SIGN_IN_SUCCESS = "SIGN_IN_SUCCESS", "Sign-in succeeded"
    SIGN_IN_FAILED = "SIGN_IN_FAILED", "First failed sign-in"
    SIGN_IN_LOCKED = "SIGN_IN_LOCKED", "Sign-in locked"
    CREDENTIAL_RESET = "CREDENTIAL_RESET", "Student credentials reset"
    STUDENT_CREATED = "STUDENT_CREATED", "Student created"
    ENROLLED = "ENROLLED", "Student enrolled"
    ENROLLMENT_ENDED = "ENROLLMENT_ENDED", "Enrollment ended"


class AuditEvent(models.Model):
    Type = AuditEventType

    organization = models.ForeignKey(
        "organizations.Organization", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    event_type = models.CharField(max_length=24)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    actor_username = models.CharField(max_length=150, blank=True)
    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    subject_username = models.CharField(max_length=150, blank=True)
    classroom_id = models.PositiveBigIntegerField(null=True, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [
            models.Index(fields=["organization", "created_at"], name="audit_org_created_idx"),
            models.Index(fields=["created_at"], name="audit_created_idx"),
        ]
        constraints = [models.CheckConstraint(
            condition=Q(event_type__in=AuditEventType.values),
            name="audit_event_type_valid",
        )]

    def save(self, *args, **kwargs):
        if self.pk is not None and not self._state.adding:
            raise ValueError("Audit events cannot be changed.")
        super().save(*args, **kwargs)
