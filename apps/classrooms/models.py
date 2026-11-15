from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower, Trim


class Classroom(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower(Trim("name")), models.F("organization"), name="classroom_org_name_ci",
            ),
            models.CheckConstraint(condition=~models.Q(name=""), name="classroom_name_nonempty"),
        ]

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Enter a class name."})
        creator = get_user_model().objects.filter(pk=self.created_by_id).first()
        if creator and (creator.organization_id != self.organization_id
                        or creator.role not in {"OWNER", "INSTRUCTOR"}):
            raise ValidationError({"created_by": "Creator must be staff in this organization."})

    def __str__(self):
        return self.name


def validate_class_link(instance, field, role):
    user = get_user_model().objects.filter(pk=getattr(instance, field + "_id")).first()
    classroom = Classroom.objects.select_related("organization").filter(
        pk=instance.classroom_id,
    ).first()
    if user is None or classroom is None:
        return
    if user.role != role or user.organization_id != classroom.organization_id:
        raise ValidationError({field: "Account role and organization must match the class."})
    if instance.is_active and (not user.is_active or not classroom.is_active
                               or not classroom.organization.is_active):
        raise ValidationError({field: "Active links require active accounts, classes and organization."})
    if role == "STUDENT" and not hasattr(user, "student_profile"):
        raise ValidationError({field: "A student profile is required."})


class ClassInstructor(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="instructor_links")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="classroom_memberships")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["classroom", "instructor"], name="classroom_instructor_unique",
        )]

    def clean(self):
        super().clean()
        validate_class_link(self, "instructor", "INSTRUCTOR")


class ClassEnrollment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="enrollment_links")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name="classroom_enrollments")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["classroom", "student"], name="classroom_student_unique",
        )]

    def clean(self):
        super().clean()
        validate_class_link(self, "student", "STUDENT")
