from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q

from apps.classrooms.policies import current_staff
from apps.classrooms.services import _lock_actor
from apps.lessons.models import LESSON_FIELDS, Lesson


def visible_lessons(actor):
    user = current_staff(actor)
    lessons = Lesson.objects.filter(organization_id=user.organization_id)
    if user.role != "OWNER":
        lessons = lessons.filter(Q(is_active=True) | Q(created_by_id=user.pk))
    return lessons


def can_manage(user, lesson):
    return (user.organization_id == lesson.organization_id
            and (user.role == "OWNER" or user.pk == lesson.created_by_id))


def checked_details(details):
    if set(details) != set(LESSON_FIELDS):
        raise ValidationError("Provide only the editable lesson fields.")
    return details


def locked_lesson(user, lesson_id, expected_version):
    lesson = Lesson.objects.select_for_update().filter(
        pk=lesson_id, organization_id=user.organization_id,
    ).first()
    if lesson is None or not can_manage(user, lesson):
        raise PermissionDenied
    if lesson.version != expected_version:
        raise ValidationError("Lesson changed. Reload before saving.")
    return lesson


@transaction.atomic
def create_lesson(*, actor, **details):
    user = _lock_actor(actor)
    lesson = Lesson(organization_id=user.organization_id, created_by=user, **checked_details(details))
    lesson.full_clean()
    lesson.save()
    return lesson


@transaction.atomic
def update_lesson(*, actor, lesson_id, expected_version, **details):
    user = _lock_actor(actor)
    lesson = locked_lesson(user, lesson_id, expected_version)
    if not lesson.is_active:
        raise ValidationError("Archived lessons cannot be edited.")
    for name, value in checked_details(details).items():
        setattr(lesson, name, value)
    lesson.version += 1
    lesson.full_clean()
    lesson.save()
    return lesson


@transaction.atomic
def archive_lesson(*, actor, lesson_id, expected_version):
    user = _lock_actor(actor)
    lesson = locked_lesson(user, lesson_id, expected_version)
    if lesson.is_active:
        lesson.is_active = False
        lesson.version += 1
        lesson.full_clean()
        lesson.save(update_fields=["is_active", "version", "updated_at"])
    return lesson
