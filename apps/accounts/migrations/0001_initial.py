import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.db.models.functions.text
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("organizations", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("role", models.CharField(choices=[("OWNER", "STEM owner"), ("INSTRUCTOR", "Instructor"), ("STUDENT", "Student")], max_length=12)),
                ("display_name", models.CharField(blank=True, max_length=100)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organizations.organization")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"constraints": [
                models.CheckConstraint(condition=models.Q(role__in=["OWNER", "INSTRUCTOR", "STUDENT"]), name="user_valid_role"),
                models.CheckConstraint(condition=models.Q(role="STUDENT") | ~models.Q(email=""), name="staff_email_required"),
                models.UniqueConstraint(django.db.models.functions.text.Lower("email"), condition=models.Q(role__in=["OWNER", "INSTRUCTOR"]), name="unique_staff_email_ci"),
            ]},
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("grade", models.CharField(choices=[("PRE_K", "Pre-K"), ("K", "Kindergarten"), ("1", "Grade 1"), ("2", "Grade 2"), ("3", "Grade 3"), ("4", "Grade 4"), ("5", "Grade 5"), ("6", "Grade 6"), ("7", "Grade 7"), ("8", "Grade 8")], max_length=5)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="student_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"constraints": [models.CheckConstraint(condition=models.Q(grade__in=["PRE_K", "K", "1", "2", "3", "4", "5", "6", "7", "8"]), name="student_valid_grade")]},
        ),
    ]
