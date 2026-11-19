from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from apps.classrooms.models import Classroom


def current_staff(actor):
    verify = getattr(actor, "is_verified", None)
    if (not settings.LMS_STAFF_AUTH_ENABLED or not getattr(actor, "is_authenticated", False)
            or not getattr(actor, "pk", None) or not callable(verify) or not verify()):
        raise PermissionDenied
    user = get_user_model().objects.select_related("organization").filter(
        pk=actor.pk, organization_id=getattr(actor, "organization_id", None),
        is_active=True, role__in=["OWNER", "INSTRUCTOR"], organization__is_active=True,
    ).first()
    if user is None:
        raise PermissionDenied
    return user


def visible_classrooms(actor):
    user = current_staff(actor)
    rooms = Classroom.objects.filter(organization_id=user.organization_id)
    if user.role == "INSTRUCTOR":
        rooms = rooms.filter(is_active=True, instructor_links__instructor_id=user.pk,
                             instructor_links__is_active=True)
    return rooms.distinct()


def visible_students(actor):
    user = current_staff(actor)
    students = get_user_model().objects.filter(
        organization_id=user.organization_id, role="STUDENT", is_active=True,
        student_profile__isnull=False,
    )
    if user.role == "INSTRUCTOR":
        students = students.filter(
            classroom_enrollments__classroom__in=visible_classrooms(actor),
            classroom_enrollments__is_active=True,
        )
    return students.distinct()


def visible_class_students(actor, classroom_id):
    if not visible_classrooms(actor).filter(pk=classroom_id, is_active=True).exists():
        raise PermissionDenied
    return visible_students(actor).filter(
        classroom_enrollments__classroom_id=classroom_id,
        classroom_enrollments__is_active=True,
    ).distinct()
