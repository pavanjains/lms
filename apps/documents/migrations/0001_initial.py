import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("lessons", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(
        name="LessonDocument",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=200)),
            ("original_name", models.CharField(max_length=200)),
            ("size", models.PositiveIntegerField()),
            ("checksum", models.CharField(max_length=64)),
            ("content", models.BinaryField(editable=False)),
            ("is_active", models.BooleanField(default=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("archived_at", models.DateTimeField(blank=True, null=True)),
            ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="supporting_documents", to="lessons.lesson")),
            ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
        ],
        options={"constraints": [models.CheckConstraint(condition=models.Q(size__gte=1, size__lte=5242880), name="document_size_bounded")]},
    )]
