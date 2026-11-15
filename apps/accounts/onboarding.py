import hashlib
from smtplib import SMTPException
from urllib.parse import urlsplit

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.invitation_services import (
    accept_instructor_invitation, issue_instructor_invitation,
)
from apps.accounts.models import InstructorInvitation
from apps.accounts.owner_views import require_owner
from apps.accounts.policies import staff_mfa_required


class DeliveryError(Exception):
    pass


class InviteForm(forms.Form):
    email = forms.EmailField(max_length=254)
    confirm = forms.BooleanField(label="Send an instructor invitation to this address.")


class ResendForm(forms.Form):
    confirm = forms.BooleanField(label="Replace the previous invitation and send a new link.")


class ActivationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned


def enabled():
    if not (settings.LMS_STAFF_AUTH_ENABLED
            and getattr(settings, "LMS_INSTRUCTOR_ONBOARDING_ENABLED", False)):
        raise Http404


def public_origin():
    origin = getattr(settings, "LMS_PUBLIC_ORIGIN", "").strip()
    parsed = urlsplit(origin)
    local_http = settings.DEBUG and parsed.scheme == "http" and parsed.hostname in {
        "localhost", "127.0.0.1", "::1",
    }
    if (not parsed.hostname or (parsed.scheme != "https" and not local_http)
            or parsed.username or parsed.password or parsed.path not in {"", "/"}
            or parsed.query or parsed.fragment):
        raise ImproperlyConfigured("Configure an approved LMS_PUBLIC_ORIGIN.")
    return origin.rstrip("/")


@transaction.atomic
def issue_and_deliver(*, actor, email):
    origin = public_origin()
    sender = getattr(settings, "LMS_INVITATION_FROM_EMAIL", "")
    validate_email(sender)
    invitation, token = issue_instructor_invitation(actor=actor, email=email)
    link = origin + reverse("onboarding:activate", args=[token])
    body = (
        "You have been invited to teach robotics. Set your credentials here:\n\n"
        + link + "\n\nThis one-time link expires at "
        + invitation.expires_at.isoformat()
        + ". Sign-in will require authenticator enrollment. Ignore unexpected invitations."
    )
    try:
        sent = EmailMessage("Robotics instructor invitation", body, sender, [invitation.email]).send()
    except (SMTPException, OSError):
        raise DeliveryError("Mail delivery failed.") from None
    if sent != 1:
        raise DeliveryError("Mail backend did not accept the message.")
    return invitation


def page(request, context, status=200):
    response = render(request, "accounts/onboarding.html", context, status=status)
    response["Referrer-Policy"] = "no-referrer"
    return response


@require_http_methods(["GET", "POST"])
@never_cache
@staff_mfa_required
def invite(request, invitation_id=None):
    enabled()
    require_owner(request.user)
    previous = None
    if invitation_id is not None:
        previous = get_object_or_404(
            InstructorInvitation, pk=invitation_id,
            organization_id=request.user.organization_id,
        )
        if previous.accepted_at:
            return page(request, {"title": "Invitation unavailable", "error": "Already accepted."}, 409)
    form_class = ResendForm if previous else InviteForm
    form = form_class(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            issue_and_deliver(
                actor=request.user, email=previous.email if previous else form.cleaned_data["email"],
            )
        except (ValidationError, DeliveryError, ImproperlyConfigured):
            form.add_error(None, "Unable to send. No invitation changes saved. Check the email or delivery configuration.")
        else:
            return page(request, {
                "title": "Invitation submitted",
                "notice": "The configured email backend accepted the message; inbox delivery is not confirmed.",
                "owner": True,
            })
    return page(request, {
        "title": "Resend instructor invitation" if previous else "Invite instructor",
        "recipient": previous.email if previous else None,
        "form": form, "owner": True,
    }, 400 if request.method == "POST" else 200)


@require_http_methods(["GET", "POST"])
@never_cache
@sensitive_post_parameters("password1", "password2")
def activate(request, token):
    enabled()
    if request.user.is_authenticated:
        return page(request, {"title": "Sign out first", "error": "Sign out before activating another account."}, 409)
    digest = hashlib.sha256(token.encode()).hexdigest() if 20 <= len(token) <= 256 else ""
    invitation = InstructorInvitation.objects.select_related("organization", "created_by").filter(
        token_digest=digest, accepted_at__isnull=True, revoked_at__isnull=True,
        expires_at__gt=timezone.now(), organization__is_active=True,
        created_by__is_active=True, created_by__role="OWNER",
    ).first()
    if invitation is None or invitation.created_by.organization_id != invitation.organization_id:
        return page(request, {"title": "Invitation unavailable", "error": "Request a new invitation from the owner."}, 400)
    form = ActivationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            accept_instructor_invitation(
                token=token, username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
        except ValidationError:
            form.add_error(None, "Unable to activate. Check the username/password or request a new invitation.")
        else:
            return redirect("onboarding:complete")
    return page(request, {"title": "Activate instructor account", "form": form},
                400 if request.method == "POST" else 200)


@require_safe
@never_cache
def complete(request):
    enabled()
    return page(request, {
        "title": "Activation complete",
        "notice": "Sign in with your invited email and new password, then enroll your authenticator.",
        "complete": True,
    })
