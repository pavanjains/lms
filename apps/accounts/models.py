from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "STEM owner"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        STUDENT = "STUDENT", "Student"

    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT)
    role = models.CharField(max_length=12, choices=Role.choices)
    display_name = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(role__in=["OWNER", "INSTRUCTOR", "STUDENT"]), name="user_valid_role"),
            models.CheckConstraint(condition=Q(role="STUDENT") | ~Q(email=""), name="staff_email_required"),
            models.UniqueConstraint(Lower("email"), condition=Q(role__in=["OWNER", "INSTRUCTOR"]), name="unique_staff_email_ci"),
        ]

    def clean(self):
        super().clean()
        self.email = self.email.strip()
        if self.role in {self.Role.OWNER, self.Role.INSTRUCTOR} and not self.email:
            raise ValidationError({"email": "Staff accounts require an email address."})

    def __str__(self):
        return self.display_name or self.username


class StudentProfile(models.Model):
    class Grade(models.TextChoices):
        PRE_K = "PRE_K", "Pre-K"
        K = "K", "Kindergarten"
        G1 = "1", "Grade 1"
        G2 = "2", "Grade 2"
        G3 = "3", "Grade 3"
        G4 = "4", "Grade 4"
        G5 = "5", "Grade 5"
        G6 = "6", "Grade 6"
        G7 = "7", "Grade 7"
        G8 = "8", "Grade 8"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="student_profile")
    grade = models.CharField(max_length=5, choices=Grade.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=Q(grade__in=["PRE_K", "K", "1", "2", "3", "4", "5", "6", "7", "8"]),
            name="student_valid_grade",
        )]

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.STUDENT:
            raise ValidationError({"user": "Student profiles require the student role."})
