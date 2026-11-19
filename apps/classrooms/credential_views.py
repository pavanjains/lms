from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.views.decorators.http import require_http_methods

from apps.accounts.policies import staff_mfa_required
from apps.classrooms.credential_services import reset_student_credentials
from apps.classrooms.forms import ConfirmationForm
from apps.classrooms.policies import visible_classrooms, visible_class_students
from apps.classrooms.views import page


@require_http_methods(["GET", "POST"])
@staff_mfa_required
@sensitive_post_parameters()
@sensitive_variables()
def student_credentials(request, classroom_id, student_id):
    room = get_object_or_404(visible_classrooms(request.user), pk=classroom_id, is_active=True)
    student = get_object_or_404(
        visible_class_students(request.user, room.pk).values("pk", "username", "display_name"),
        pk=student_id,
    )
    form = ConfirmationForm(request.POST if request.method == "POST" else None)
    credentials = None
    if request.method == "POST" and form.is_valid():
        try:
            credentials = reset_student_credentials(
                actor=request.user, classroom_id=room.pk, student_id=student["pk"],
            )
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to reset credentials. No changes saved. Check configuration or reload and retry.")
        else:
            form = None
    response = page(request, "credentials.html", {
        "room": room, "student": student, "form": form, "credentials": credentials,
    }, 400 if request.method == "POST" and form is not None else 200)
    response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    response["Content-Security-Policy"] = (
        "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    )
    return response
