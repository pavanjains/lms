import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0002_lessonassignment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="lessonassignment",
            name="progress",
            field=models.CharField(
                choices=[("ASSIGNED", "Assigned"), ("IN_PROGRESS", "In progress"),
                         ("REVIEWED", "Reviewed"), ("NEEDS_REVISION", "Needs revision")],
                default="ASSIGNED", max_length=20),
        ),
        migrations.AddField(
            model_name="lessonassignment",
            name="feedback",
            field=models.TextField(blank=True, default="", max_length=2000),
        ),
        migrations.AddField(
            model_name="lessonassignment",
            name="progress_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="lessonassignment",
            name="progress_updated_by",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="progress_updated_lesson_assignments", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name="lessonassignment",
            constraint=models.CheckConstraint(
                condition=models.Q(progress__in=["ASSIGNED", "IN_PROGRESS", "REVIEWED", "NEEDS_REVISION"]),
                name="assignment_valid_progress"),
        ),
        migrations.AddConstraint(
            model_name="lessonassignment",
            constraint=models.CheckConstraint(
                condition=(models.Q(progress_updated_at__isnull=True, progress_updated_by__isnull=True)
                           | models.Q(progress_updated_at__isnull=False, progress_updated_by__isnull=False)),
                name="assignment_progress_update_pair"),
        ),
    ]
