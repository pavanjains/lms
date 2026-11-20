from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models

GRADE_CHOICES = [(-1, "Pre-K"), (0, "Kindergarten")] + [(n, f"Grade {n}") for n in range(1, 9)]
LESSON_FIELDS = ("title", "summary", "lego_url", "instructions", "kit", "min_grade", "max_grade")


def validate_lego_url(value):
    URLValidator(schemes=["https"])(value)
    try:
        parts = urlsplit(value)
        valid = (parts.scheme == "https" and parts.hostname == "education.lego.com"
                 and parts.port in {None, 443} and not parts.username and not parts.password)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise ValidationError("Use an HTTPS education.lego.com link without embedded credentials.")
    return value


class Lesson(models.Model):
    class Kit(models.TextChoices):
        ESSENTIAL = "ESSENTIAL", "SPIKE Essential"
        PRIME = "PRIME", "SPIKE Prime"

    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, max_length=2000)
    lego_url = models.URLField(max_length=1000)
    instructions = models.TextField(max_length=20000)
    kit = models.CharField(max_length=10, choices=Kit.choices)
    min_grade = models.SmallIntegerField(choices=GRADE_CHOICES)
    max_grade = models.SmallIntegerField(choices=GRADE_CHOICES)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "is_active", "kit"], name="lesson_org_active_kit_idx")]
        constraints = [
            models.CheckConstraint(condition=models.Q(min_grade__gte=-1, max_grade__lte=8,
                                                       min_grade__lte=models.F("max_grade")), name="lesson_valid_grade_range"),
            models.CheckConstraint(condition=(models.Q(kit="ESSENTIAL", max_grade__lte=4)
                                               | models.Q(kit="PRIME", min_grade__gte=4)), name="lesson_kit_grade_match"),
            models.CheckConstraint(condition=~models.Q(title=""), name="lesson_title_nonempty"),
            models.CheckConstraint(condition=models.Q(version__gte=1), name="lesson_version_positive"),
        ]

    def clean(self):
        super().clean()
        self.title = (self.title or "").strip()
        self.instructions = (self.instructions or "").strip()
        if not self.title or not self.instructions:
            raise ValidationError("Title and instructions must not be blank.")
        try:
            validate_lego_url(self.lego_url)
        except ValidationError as exc:
            raise ValidationError({"lego_url": exc.messages}) from None
        if isinstance(self.min_grade, int) and isinstance(self.max_grade, int):
            if (not -1 <= self.min_grade <= self.max_grade <= 8
                    or (self.kit == self.Kit.ESSENTIAL and self.max_grade > 4)
                    or (self.kit == self.Kit.PRIME and self.min_grade < 4)):
                raise ValidationError("Essential supports through Grade 4; Prime supports Grades 4–8.")
        creator = get_user_model().objects.filter(pk=self.created_by_id).first()
        if creator and (creator.organization_id != self.organization_id
                        or creator.role not in {"OWNER", "INSTRUCTOR"}):
            raise ValidationError({"created_by": "Creator must be staff in this organization."})

    def __str__(self):
        return self.title


class LessonAssignment(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT)
    classroom = models.ForeignKey("classrooms.Classroom", on_delete=models.PROTECT)
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name="lesson_assignments")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="issued_lesson_assignments")
    lesson_version = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, max_length=2000)
    lego_url = models.URLField(max_length=1000)
    instructions = models.TextField(max_length=20000)
    kit = models.CharField(max_length=10, choices=Lesson.Kit.choices)
    min_grade = models.SmallIntegerField(choices=GRADE_CHOICES)
    max_grade = models.SmallIntegerField(choices=GRADE_CHOICES)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                     null=True, blank=True, related_name="cancelled_lesson_assignments")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "student", "lesson"],
                condition=models.Q(cancelled_at__isnull=True), name="assignment_one_active_lesson",
            ),
            models.CheckConstraint(
                condition=(models.Q(cancelled_at__isnull=True, cancelled_by__isnull=True)
                           | models.Q(cancelled_at__isnull=False, cancelled_by__isnull=False)),
                name="assignment_cancellation_pair",
            ),
            models.CheckConstraint(condition=models.Q(version__gte=1, lesson_version__gte=1),
                                   name="assignment_positive_versions"),
        ]

    def clean(self):
        super().clean()
        snapshot = {name: getattr(self, name) for name in LESSON_FIELDS}
        Lesson(organization_id=self.organization_id, created_by_id=self.created_by_id,
               **snapshot).full_clean()
        if self.classroom_id and self.classroom.organization_id != self.organization_id:
            raise ValidationError("Class and assignment organization must match.")
        if self.lesson_id and self.lesson.organization_id != self.organization_id:
            raise ValidationError("Lesson and assignment organization must match.")
        if self.student_id and (self.student.role != "STUDENT"
                                or self.student.organization_id != self.organization_id):
            raise ValidationError("Recipient must be a student in this organization.")
        if self.cancelled_by_id and (self.cancelled_by.role not in {"OWNER", "INSTRUCTOR"}
                                    or self.cancelled_by.organization_id != self.organization_id):
            raise ValidationError("Cancelling staff must belong to this organization.")
