import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("organizations", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(
        name="Lesson",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=200)),
            ("summary", models.TextField(blank=True, max_length=2000)),
            ("lego_url", models.URLField(max_length=1000)),
            ("instructions", models.TextField(max_length=20000)),
            ("kit", models.CharField(choices=[("ESSENTIAL", "SPIKE Essential"), ("PRIME", "SPIKE Prime")], max_length=10)),
            ("min_grade", models.SmallIntegerField(choices=[(-1, "Pre-K"), (0, "Kindergarten"), (1, "Grade 1"), (2, "Grade 2"), (3, "Grade 3"), (4, "Grade 4"), (5, "Grade 5"), (6, "Grade 6"), (7, "Grade 7"), (8, "Grade 8")])),
            ("max_grade", models.SmallIntegerField(choices=[(-1, "Pre-K"), (0, "Kindergarten"), (1, "Grade 1"), (2, "Grade 2"), (3, "Grade 3"), (4, "Grade 4"), (5, "Grade 5"), (6, "Grade 6"), (7, "Grade 7"), (8, "Grade 8")])),
            ("is_active", models.BooleanField(default=True)),
            ("version", models.PositiveIntegerField(default=1)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organizations.organization")),
            ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
        ],
        options={
            "indexes": [models.Index(fields=["organization", "is_active", "kit"], name="lesson_org_active_kit_idx")],
            "constraints": [
                models.CheckConstraint(condition=models.Q(min_grade__gte=-1, max_grade__lte=8, min_grade__lte=models.F("max_grade")), name="lesson_valid_grade_range"),
                models.CheckConstraint(condition=(models.Q(kit="ESSENTIAL", max_grade__lte=4) | models.Q(kit="PRIME", min_grade__gte=4)), name="lesson_kit_grade_match"),
                models.CheckConstraint(condition=~models.Q(title=""), name="lesson_title_nonempty"),
                models.CheckConstraint(condition=models.Q(version__gte=1), name="lesson_version_positive"),
            ],
        },
    )]
