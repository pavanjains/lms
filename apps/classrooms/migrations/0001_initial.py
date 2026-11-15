import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models.functions import Lower, Trim


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("organizations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Classroom",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organizations.organization")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={"constraints": [
                models.UniqueConstraint(Lower(Trim("name")), models.F("organization"), name="classroom_org_name_ci"),
                models.CheckConstraint(condition=~models.Q(name=""), name="classroom_name_nonempty"),
            ]},
        ),
        migrations.CreateModel(
            name="ClassInstructor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="instructor_links", to="classrooms.classroom")),
                ("instructor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="classroom_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={"constraints": [models.UniqueConstraint(fields=["classroom", "instructor"], name="classroom_instructor_unique")]},
        ),
        migrations.CreateModel(
            name="ClassEnrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollment_links", to="classrooms.classroom")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="classroom_enrollments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"constraints": [models.UniqueConstraint(fields=["classroom", "student"], name="classroom_student_unique")]},
        ),
    ]
