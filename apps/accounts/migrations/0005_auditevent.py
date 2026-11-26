import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0004_loginthrottle")]
    operations = [
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=24)),
                ("actor_username", models.CharField(blank=True, max_length=150)),
                ("subject_username", models.CharField(blank=True, max_length=150)),
                ("classroom_id", models.PositiveBigIntegerField(blank=True, null=True)),
                ("detail", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+", to=settings.AUTH_USER_MODEL,
                )),
                ("organization", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+", to="organizations.organization",
                )),
                ("subject", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+", to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-created_at", "-pk"]},
        ),
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["organization", "created_at"], name="audit_org_created_idx"),
        ),
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["created_at"], name="audit_created_idx"),
        ),
        migrations.AddConstraint(
            model_name="auditevent",
            constraint=models.CheckConstraint(
                condition=models.Q(("event_type__in", [
                    "SIGN_IN_SUCCESS", "SIGN_IN_FAILED", "SIGN_IN_LOCKED", "CREDENTIAL_RESET",
                    "STUDENT_CREATED", "ENROLLED", "ENROLLMENT_ENDED",
                ])),
                name="audit_event_type_valid",
            ),
        ),
    ]
