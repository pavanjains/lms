import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.CreateModel(
        name="InstructorInvitation",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("email", models.EmailField(max_length=254)),
            ("token_digest", models.CharField(editable=False, max_length=64, unique=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("expires_at", models.DateTimeField()),
            ("revoked_at", models.DateTimeField(blank=True, null=True)),
            ("accepted_at", models.DateTimeField(blank=True, null=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organizations.organization")),
            ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="issued_invitations", to=settings.AUTH_USER_MODEL)),
            ("accepted_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="accepted_invitations", to=settings.AUTH_USER_MODEL)),
        ],
        options={
            "indexes": [models.Index(fields=["organization", "email"], name="invite_org_email_idx")],
            "constraints": [
                models.CheckConstraint(condition=models.Q(accepted_at__isnull=True) | models.Q(revoked_at__isnull=True), name="invite_not_accepted_revoked"),
                models.CheckConstraint(condition=(models.Q(accepted_at__isnull=True, accepted_user__isnull=True) | models.Q(accepted_at__isnull=False, accepted_user__isnull=False)), name="invite_acceptance_pair"),
            ],
        },
    )]
