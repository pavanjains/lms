from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

from apps.accounts.policies import staff_mfa_required
from apps.classrooms.policies import visible_classrooms
from apps.classrooms.student_forms import StudentCreationForm
from apps.classrooms.student_services import create_student_in_class
from apps.classrooms.views import page


@require_http_methods(["GET", "POST"])
@staff_mfa_required
@sensitive_post_parameters()
def student_create(request, classroom_id):
    room = get_object_or_404(visible_classrooms(request.user), pk=classroom_id, is_active=True)
    form = StudentCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            create_student_in_class(
                actor=request.user, classroom_id=room.pk,
                username=form.cleaned_data["username"],
                display_name=form.cleaned_data["display_name"], grade=form.cleaned_data["grade"],
                password=form.cleaned_data["password1"],
            )
        except ValidationError:
            form.add_error(None, "Unable to create student. Check the details/password or choose another username.")
        else:
            messages.success(request, "Student account created and enrolled. Student sign-in is not available yet.")
            return redirect("classrooms:detail", classroom_id=room.pk)
    return page(request, "student_form.html", {"room": room, "form": form},
                400 if request.method == "POST" else 200)
