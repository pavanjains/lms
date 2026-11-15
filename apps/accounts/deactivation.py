from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.accounts.invitation_services import _lock_owner_organization
from apps.accounts.owner_views import require_owner
from apps.accounts.policies import staff_mfa_required


class DeactivationForm(forms.Form):
    confirm = forms.BooleanField(label="I confirm this instructor should lose staff access.")


@transaction.atomic
def deactivate_instructor(*, actor, instructor_id):
    organization = _lock_owner_organization(actor)
    if settings.SESSION_ENGINE != "django.contrib.sessions.backends.db":
        raise ValidationError("Deactivation requires the database session backend.")
    instructor = get_user_model().objects.select_for_update().filter(
        pk=instructor_id, organization=organization, role="INSTRUCTOR",
    ).first()
    if instructor is None:
        raise PermissionDenied
    if instructor.is_active:
        instructor.is_active = False
        instructor.save(update_fields=["is_active"])
    keys = []
    for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator(chunk_size=100):
        if str(session.get_decoded().get(SESSION_KEY, "")) == str(instructor.pk):
            keys.append(session.session_key)
    if keys:
        Session.objects.filter(session_key__in=keys).delete()
    return instructor


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def deactivate(request, instructor_id):
    require_owner(request.user)
    instructor = get_object_or_404(
        get_user_model(), pk=instructor_id,
        organization_id=request.user.organization_id, role="INSTRUCTOR",
    )
    form = DeactivationForm(request.POST if request.method == "POST" else None)
    error = None
    status = 200
    if request.method == "POST":
        if form.is_valid():
            try:
                deactivate_instructor(actor=request.user, instructor_id=instructor.pk)
            except ValidationError:
                error = "Deactivation is unavailable with the current session configuration. No changes saved."
                status = 409
            else:
                messages.success(request, "Instructor deactivated; existing database sessions revoked.")
                return redirect("owner-accounts:instructors")
        else:
            status = 400
    return render(request, "accounts/deactivate_instructor.html", {
        "instructor": instructor, "form": form, "error": error,
    }, status=status)
