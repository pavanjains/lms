from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_installation_mfa_policy")]
    operations = [
        migrations.CreateModel(
            name="LoginThrottle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope", models.CharField(max_length=10)),
                ("key_digest", models.CharField(max_length=64)),
                ("failures", models.PositiveIntegerField(default=0)),
                ("window_started_at", models.DateTimeField()),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name="loginthrottle",
            index=models.Index(fields=["window_started_at"], name="login_throttle_window_idx"),
        ),
        migrations.AddConstraint(
            model_name="loginthrottle",
            constraint=models.UniqueConstraint(fields=("scope", "key_digest"), name="login_throttle_unique_key"),
        ),
        migrations.AddConstraint(
            model_name="loginthrottle",
            constraint=models.CheckConstraint(
                condition=models.Q(("scope__in", ["student", "staff"])), name="login_throttle_valid_scope",
            ),
        ),
    ]
