from django.conf import settings
from django.db import models


class InstallationMfaPolicy(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    require_mfa = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(id=1), name="mfa_policy_singleton"),
            models.CheckConstraint(condition=models.Q(version__gte=1), name="mfa_policy_version_positive"),
        ]


class InstallationMfaPolicyAudit(models.Model):
    policy_version = models.PositiveIntegerField(unique=True)
    previous_required = models.BooleanField()
    new_required = models.BooleanField()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    actor_username = models.CharField(max_length=150)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-policy_version"]
        constraints = [
            models.CheckConstraint(condition=models.Q(policy_version__gte=2), name="mfa_audit_version_valid"),
            models.CheckConstraint(
                condition=~models.Q(previous_required=models.F("new_required")),
                name="mfa_audit_records_change",
            ),
        ]
