import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0001_initial"), ("classrooms", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [migrations.CreateModel(
        name="LessonAssignment",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("lesson_version", models.PositiveIntegerField()),
            ("title", models.CharField(max_length=200)),
            ("summary", models.TextField(blank=True, max_length=2000)),
            ("lego_url", models.URLField(max_length=1000)),
            ("instructions", models.TextField(max_length=20000)),
            ("kit", models.CharField(choices=[("ESSENTIAL", "SPIKE Essential"), ("PRIME", "SPIKE Prime")], max_length=10)),
            ("min_grade", models.SmallIntegerField(choices=[(-1, "Pre-K"), (0, "Kindergarten")] + [(n, f"Grade {n}") for n in range(1, 9)])),
            ("max_grade", models.SmallIntegerField(choices=[(-1, "Pre-K"), (0, "Kindergarten")] + [(n, f"Grade {n}") for n in range(1, 9)])),
            ("version", models.PositiveIntegerField(default=1)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("cancelled_at", models.DateTimeField(blank=True, null=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organizations.organization")),
            ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="classrooms.classroom")),
            ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="lessons.lesson")),
            ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lesson_assignments", to=settings.AUTH_USER_MODEL)),
            ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="issued_lesson_assignments", to=settings.AUTH_USER_MODEL)),
            ("cancelled_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="cancelled_lesson_assignments", to=settings.AUTH_USER_MODEL)),
        ],
        options={"constraints": [
            models.UniqueConstraint(fields=("classroom", "student", "lesson"), condition=models.Q(cancelled_at__isnull=True), name="assignment_one_active_lesson"),
            models.CheckConstraint(condition=(models.Q(cancelled_at__isnull=True, cancelled_by__isnull=True) | models.Q(cancelled_at__isnull=False, cancelled_by__isnull=False)), name="assignment_cancellation_pair"),
            models.CheckConstraint(condition=models.Q(version__gte=1, lesson_version__gte=1), name="assignment_positive_versions"),
        ]},
    )]
