from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.invitation_services import revoke_instructor_invitation
from apps.accounts.models import InstructorInvitation
from apps.accounts.policies import staff_mfa_required


class RevokeInvitationForm(forms.Form):
    confirm = forms.BooleanField(label="I confirm this invitation should be revoked.")


def require_owner(user):
    if user.role != "OWNER":
        raise PermissionDenied


def invitation_status(invitation, now):
    if invitation.accepted_at:
        return "Accepted"
    if invitation.revoked_at:
        return "Revoked"
    if invitation.expires_at <= now:
        return "Expired"
    return "Pending"


@require_safe
@staff_mfa_required
def instructor_management(request):
    require_owner(request.user)
    search = request.GET.get("q", "").strip()[:100]
    instructors = get_user_model().objects.filter(
        organization_id=request.user.organization_id, role="INSTRUCTOR",
    ).order_by("username", "pk")
    invitations = InstructorInvitation.objects.filter(
        organization_id=request.user.organization_id,
    ).order_by("-created_at", "-pk")
    if search:
        instructors = instructors.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
            | Q(display_name__icontains=search)
        )
        invitations = invitations.filter(email__icontains=search)
    instructor_page = Paginator(instructors, 25).get_page(request.GET.get("instructor_page"))
    invitation_page = Paginator(invitations, 25).get_page(request.GET.get("invitation_page"))
    now = timezone.now()
    for invitation in invitation_page:
        invitation.display_status = invitation_status(invitation, now)
        invitation.can_revoke = not invitation.accepted_at and not invitation.revoked_at
    return render(request, "accounts/owner_instructors.html", {
        "search": search, "instructor_page": instructor_page,
        "invitation_page": invitation_page,
    })


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def revoke_invitation(request, invitation_id):
    require_owner(request.user)
    invitation = get_object_or_404(
        InstructorInvitation, pk=invitation_id,
        organization_id=request.user.organization_id,
    )
    form = RevokeInvitationForm(request.POST if request.method == "POST" else None)
    error = None
    status = 200
    if invitation.accepted_at or invitation.revoked_at:
        error = "This invitation has already been accepted or revoked."
        status = 409
    elif request.method == "POST":
        if form.is_valid():
            try:
                revoke_instructor_invitation(actor=request.user, invitation_id=invitation.pk)
            except ValidationError:
                error = "The invitation changed before this request completed. Refresh the list."
                status = 409
            else:
                messages.success(request, "Invitation revoked.")
                return redirect("owner-accounts:instructors")
        else:
            status = 400
    return render(request, "accounts/revoke_invitation.html", {
        "invitation": invitation, "form": form, "error": error,
    }, status=status)
