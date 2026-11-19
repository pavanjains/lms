from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment
from apps.classrooms.services import _lock_actor, _lock_room


def create_student_in_class(*, actor, classroom_id, username, display_name, grade, password):
    try:
        with transaction.atomic():
            staff = _lock_actor(actor)
            room = _lock_room(staff, classroom_id)
            if (not all(isinstance(value, str) for value in
                        (username, display_name, grade, password))
                    or not username.strip() or not display_name.strip() or not password
                    or len(password) > 128):
                raise ValidationError("Invalid student details.")
            User = get_user_model()
            student = User(
                organization_id=staff.organization_id, role="STUDENT",
                username=User.normalize_username(username.strip()),
                display_name=display_name.strip(), email="",
                is_active=True, is_staff=False, is_superuser=False,
            )
            validate_password(password, user=student)
            student.set_password(password)
            student.full_clean()
            student.save()
            profile = StudentProfile(user=student, grade=grade)
            profile.full_clean()
            profile.save()
            enrollment = ClassEnrollment(classroom=room, student=student)
            enrollment.full_clean()
            enrollment.save()
            return student
    except (ValidationError, IntegrityError):
        raise ValidationError(
            "Unable to create student. Check the details/password or choose another username."
        ) from None
