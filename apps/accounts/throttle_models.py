from django.db import models
from django.db.models import Q


class LoginThrottle(models.Model):
    """Failed sign-in counter per submitted name. The name is stored only as a digest."""

    scope = models.CharField(max_length=10)
    key_digest = models.CharField(max_length=64)
    failures = models.PositiveIntegerField(default=0)
    window_started_at = models.DateTimeField()
    locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["window_started_at"], name="login_throttle_window_idx")]
        constraints = [
            models.UniqueConstraint(fields=["scope", "key_digest"], name="login_throttle_unique_key"),
            models.CheckConstraint(
                condition=Q(scope__in=["student", "staff"]), name="login_throttle_valid_scope",
            ),
        ]
