from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts import audit
from apps.accounts.audit_models import AuditEventType
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.classrooms.policies import current_staff, visible_students
from apps.organizations.models import Organization


def _lock_actor(actor, *, owner_only=False):
    snapshot = current_staff(actor)
    organization = Organization.objects.select_for_update().filter(
        pk=snapshot.organization_id, is_active=True,
    ).first()
    if organization is None:
        raise PermissionDenied
    user = get_user_model().objects.select_for_update().filter(
        pk=snapshot.pk, organization=organization, is_active=True,
        role__in=["OWNER", "INSTRUCTOR"],
    ).first()
    if user is None or (owner_only and user.role != "OWNER"):
        raise PermissionDenied
    return user


def _lock_room(user, classroom_id, *, active=True):
    room = Classroom.objects.select_for_update().filter(
        pk=classroom_id, organization_id=user.organization_id,
    ).first()
    if room is None or (active and not room.is_active):
        raise PermissionDenied
    if user.role != "OWNER" and not ClassInstructor.objects.filter(
        classroom=room, instructor=user, is_active=True,
    ).exists():
        raise PermissionDenied
    return room


def _target(user, target_id, role, *, active):
    target = get_user_model().objects.select_for_update().filter(
        pk=target_id, organization_id=user.organization_id, role=role,
    ).first()
    if target is None or (active and not target.is_active):
        raise PermissionDenied
    return target


def _set_link(model, room, field, target, active):
    lookup = {"classroom": room, field: target}
    link = model.objects.select_for_update().filter(**lookup).first()
    if link is None:
        if not active:
            return None
        link = model(**lookup)
    link.is_active = active
    link.full_clean()
    link.save()
    return link


def _enrollment_active(room, student):
    return ClassEnrollment.objects.filter(classroom=room, student=student, is_active=True).exists()


@transaction.atomic
def create_classroom(*, actor, name, description=""):
    user = _lock_actor(actor, owner_only=True)
    room = Classroom(organization_id=user.organization_id, name=name,
                     description=description, created_by=user)
    room.full_clean()
    room.save()
    return room


@transaction.atomic
def archive_classroom(*, actor, classroom_id):
    user = _lock_actor(actor, owner_only=True)
    room = _lock_room(user, classroom_id, active=False)
    room.is_active = False
    room.full_clean()
    room.save(update_fields=["is_active", "updated_at"])
    return room


@transaction.atomic
def assign_instructor(*, actor, classroom_id, instructor_id):
    user = _lock_actor(actor, owner_only=True)
    room = _lock_room(user, classroom_id)
    target = _target(user, instructor_id, "INSTRUCTOR", active=True)
    return _set_link(ClassInstructor, room, "instructor", target, True)


@transaction.atomic
def remove_instructor(*, actor, classroom_id, instructor_id):
    user = _lock_actor(actor, owner_only=True)
    room = _lock_room(user, classroom_id, active=False)
    target = _target(user, instructor_id, "INSTRUCTOR", active=False)
    return _set_link(ClassInstructor, room, "instructor", target, False)


@transaction.atomic
def enroll_student(*, actor, classroom_id, student_id):
    user = _lock_actor(actor)
    room = _lock_room(user, classroom_id)
    target = _target(user, student_id, "STUDENT", active=True)
    if user.role != "OWNER" and not visible_students(actor).filter(pk=target.pk).exists():
        raise PermissionDenied
    was_active = _enrollment_active(room, target)
    link = _set_link(ClassEnrollment, room, "student", target, True)
    if not was_active:
        audit.record(
            AuditEventType.ENROLLED, actor=user, subject=target, classroom_id=room.pk,
            detail={"classroom_name": room.name[:150]},
        )
    return link


@transaction.atomic
def end_enrollment(*, actor, classroom_id, student_id):
    user = _lock_actor(actor)
    room = _lock_room(user, classroom_id, active=False)
    if user.role != "OWNER" and not room.is_active:
        raise PermissionDenied
    target = _target(user, student_id, "STUDENT", active=False)
    was_active = _enrollment_active(room, target)
    link = _set_link(ClassEnrollment, room, "student", target, False)
    if was_active:
        audit.record(
            AuditEventType.ENROLLMENT_ENDED, actor=user, subject=target, classroom_id=room.pk,
            detail={"classroom_name": room.name[:150]},
        )
    return link
