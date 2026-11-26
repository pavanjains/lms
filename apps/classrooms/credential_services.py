import secrets
from dataclasses import dataclass, field

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables

from apps.accounts import throttle
from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment
from apps.classrooms.services import _lock_actor, _lock_room, _target


@dataclass(frozen=True)
class IssuedStudentCredentials:
    username: str
    password: str = field(repr=False)


@sensitive_variables()
@transaction.atomic
def reset_student_credentials(*, actor, classroom_id, student_id):
    staff = _lock_actor(actor)
    room = _lock_room(staff, classroom_id)
    student = _target(staff, student_id, "STUDENT", active=True)
    if (not StudentProfile.objects.filter(user=student).exists()
            or not ClassEnrollment.objects.filter(
                classroom=room, student=student, is_active=True,
            ).exists()):
        raise PermissionDenied
    if settings.SESSION_ENGINE != "django.contrib.sessions.backends.db":
        raise ValidationError("Credential reset requires the database session backend.")
    password = secrets.token_urlsafe(18)
    validate_password(password, user=student)
    student.set_password(password)
    student.full_clean()
    student.save(update_fields=["password"])
    keys = []
    for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator(chunk_size=100):
        if str(session.get_decoded().get(SESSION_KEY, "")) == str(student.pk):
            keys.append(session.session_key)
    if keys:
        Session.objects.filter(session_key__in=keys).delete()
    throttle.reset(throttle.STUDENT, student.username)
    return IssuedStudentCredentials(username=student.username, password=password)
