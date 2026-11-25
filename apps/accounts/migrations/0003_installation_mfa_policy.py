import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_required_policy(apps, schema_editor):
    Policy = apps.get_model("accounts", "InstallationMfaPolicy")
    Policy.objects.using(schema_editor.connection.alias).get_or_create(
        pk=1, defaults={"require_mfa": True, "version": 1},
    )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_instructorinvitation")]
    operations = [
        migrations.CreateModel(
            name="InstallationMfaPolicy",
            fields=[
                ("id", models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ("require_mfa", models.BooleanField(default=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"constraints": [
                models.CheckConstraint(condition=models.Q(id=1), name="mfa_policy_singleton"),
                models.CheckConstraint(condition=models.Q(version__gte=1), name="mfa_policy_version_positive"),
            ]},
        ),
        migrations.CreateModel(
            name="InstallationMfaPolicyAudit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("policy_version", models.PositiveIntegerField(unique=True)),
                ("previous_required", models.BooleanField()),
                ("new_required", models.BooleanField()),
                ("actor_username", models.CharField(max_length=150)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-policy_version"], "constraints": [
                models.CheckConstraint(condition=models.Q(policy_version__gte=2), name="mfa_audit_version_valid"),
                models.CheckConstraint(condition=~models.Q(previous_required=models.F("new_required")), name="mfa_audit_records_change"),
            ]},
        ),
        migrations.RunPython(seed_required_policy, migrations.RunPython.noop),
    ]
