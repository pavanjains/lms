from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import StudentProfile
from apps.accounts.students import enabled, students
from apps.classrooms.models import ClassEnrollment
from apps.classrooms.policies import visible_classrooms
from apps.classrooms.services import _lock_actor, _lock_room
from apps.lessons.models import LESSON_FIELDS, Lesson, LessonAssignment

GRADE_NUMBERS = {"PRE_K": -1, "K": 0, **{str(n): n for n in range(1, 9)}}
PROGRESS_VALUES = {choice.value for choice in LessonAssignment.Progress}
FEEDBACK_MAX_LENGTH = 2000


def staff_assignments(actor):
    return LessonAssignment.objects.filter(
        classroom__in=visible_classrooms(actor),
    ).order_by("-created_at", "-pk")


def student_assignments(actor):
    if not enabled() or not getattr(actor, "is_authenticated", False):
        raise PermissionDenied
    user = students().filter(
        pk=getattr(actor, "pk", None), organization_id=getattr(actor, "organization_id", None),
    ).first()
    if user is None:
        raise PermissionDenied
    return LessonAssignment.objects.filter(
        student_id=user.pk, organization_id=user.organization_id, cancelled_at__isnull=True,
        organization__is_active=True, student__is_active=True, student__role="STUDENT",
        student__is_staff=False, student__is_superuser=False,
        student__organization_id=user.organization_id, student__student_profile__isnull=False,
        classroom__is_active=True, classroom__organization_id=user.organization_id,
        classroom__enrollment_links__student_id=user.pk,
        classroom__enrollment_links__is_active=True,
    ).order_by("-created_at", "-pk")


@transaction.atomic
def create_assignments(*, actor, classroom_id, lesson_id, student_ids, expected_lesson_version):
    user = _lock_actor(actor)
    room = _lock_room(user, classroom_id)
    if (not isinstance(student_ids, (list, tuple)) or not student_ids
            or any(type(pk) is not int or pk < 1 for pk in student_ids)
            or len(set(student_ids)) != len(student_ids)):
        raise ValidationError("Select a nonempty list of distinct student IDs.")
    if type(expected_lesson_version) is not int or expected_lesson_version < 1:
        raise ValidationError("Provide the reviewed lesson version.")
    lesson = Lesson.objects.select_for_update().filter(
        pk=lesson_id, organization_id=user.organization_id,
    ).first()
    if lesson is None:
        raise PermissionDenied
    if not lesson.is_active or lesson.version != expected_lesson_version:
        raise ValidationError("Lesson changed or was archived. Review before assigning.")
    lesson.full_clean()
    recipients = list(get_user_model().objects.select_for_update().filter(
        pk__in=student_ids, organization_id=user.organization_id, role="STUDENT",
        is_active=True, is_staff=False, is_superuser=False,
    ).order_by("pk"))
    enrolled = set(ClassEnrollment.objects.select_for_update().filter(
        classroom=room, student_id__in=student_ids, is_active=True,
    ).values_list("student_id", flat=True))
    if {student.pk for student in recipients} != set(student_ids) or enrolled != set(student_ids):
        raise PermissionDenied
    profiles = {profile.user_id: profile for profile in StudentProfile.objects.select_for_update().filter(
        user_id__in=student_ids,
    ).order_by("user_id")}
    for student in recipients:
        profile = profiles.get(student.pk)
        grade = GRADE_NUMBERS.get(profile.grade) if profile else None
        if grade is None or not lesson.min_grade <= grade <= lesson.max_grade:
            raise ValidationError("Every selected student must have a compatible grade and kit.")
    if LessonAssignment.objects.filter(
        classroom=room, lesson=lesson, student_id__in=student_ids, cancelled_at__isnull=True,
    ).exists():
        raise ValidationError("A selected student already has this active lesson in this class.")
    snapshot = {name: getattr(lesson, name) for name in LESSON_FIELDS}
    assignments = []
    for student in recipients:
        assignment = LessonAssignment(
            organization_id=user.organization_id, classroom=room, student=student,
            lesson=lesson, created_by=user, lesson_version=lesson.version, **snapshot,
        )
        assignment.full_clean()
        assignment.save()
        assignments.append(assignment)
    return assignments


@transaction.atomic
def cancel_assignment(*, actor, assignment_id, expected_version):
    user = _lock_actor(actor)
    assignment = LessonAssignment.objects.select_for_update().filter(
        pk=assignment_id, organization_id=user.organization_id,
    ).first()
    if assignment is None:
        raise PermissionDenied
    room = _lock_room(user, assignment.classroom_id, active=False)
    if not room.is_active and user.role != "OWNER":
        raise PermissionDenied
    if type(expected_version) is not int or assignment.version != expected_version:
        raise ValidationError("Assignment changed. Reload before cancelling.")
    if assignment.cancelled_at is None:
        assignment.cancelled_at = timezone.now()
        assignment.cancelled_by = user
        assignment.version += 1
        assignment.full_clean()
        assignment.save(update_fields=["cancelled_at", "cancelled_by", "version"])
    return assignment


@transaction.atomic
def update_progress(*, actor, assignment_id, progress, feedback, expected_version):
    user = _lock_actor(actor)
    assignment = LessonAssignment.objects.select_for_update().filter(
        pk=assignment_id, organization_id=user.organization_id,
    ).first()
    if assignment is None:
        raise PermissionDenied
    _lock_room(user, assignment.classroom_id)
    if assignment.cancelled_at is not None:
        raise ValidationError("Cancelled assignments cannot change progress.")
    if type(expected_version) is not int or assignment.version != expected_version:
        raise ValidationError("Assignment changed. Reload before updating progress.")
    if type(progress) is not str or progress not in PROGRESS_VALUES:
        raise ValidationError("Choose a valid progress status.")
    if type(feedback) is not str:
        raise ValidationError("Feedback must be text.")
    feedback = feedback.strip()
    if len(feedback) > FEEDBACK_MAX_LENGTH:
        raise ValidationError(f"Feedback must be at most {FEEDBACK_MAX_LENGTH} characters.")
    assignment.progress = progress
    assignment.feedback = feedback
    assignment.progress_updated_at = timezone.now()
    assignment.progress_updated_by = user
    assignment.version += 1
    assignment.full_clean()
    assignment.save(update_fields=[
        "progress", "feedback", "progress_updated_at", "progress_updated_by", "version",
    ])
    return assignment
