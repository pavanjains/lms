import secrets

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.crypto import constant_time_compare
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.views.decorators.http import require_http_methods

from apps.accounts import mfa_policy

REVIEW_KEY = "installation_mfa_policy_review"
REVIEW_SALT = "accounts.installation-mfa-policy.v1"
REVIEW_SECONDS = 300


class MfaPolicySelectionForm(forms.Form):
    require_mfa = forms.BooleanField(
        required=False, label="Require MFA for all staff in every organization",
    )
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class MfaPolicyConfirmationForm(forms.Form):
    token = forms.CharField(max_length=4096, widget=forms.HiddenInput)
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={
        "autocomplete": "current-password",
    }))
    confirm = forms.BooleanField(label="I confirm this affects every organization in this installation")


def selection_context(actor):
    if not mfa_policy.may_manage_policy(actor):
        return {}
    try:
        policy = mfa_policy.read_policy()
        mfa_policy.require_policy_mfa(actor, policy)
    except (ValidationError, DatabaseError):
        return {"mfa_policy_unavailable": True}
    except PermissionDenied:
        return {}
    return {"mfa_policy": policy, "mfa_selection_form": MfaPolicySelectionForm(initial={
        "require_mfa": policy.require_mfa, "expected_version": policy.version,
    })}


def page(request, *, policy=None, mode="select", status=200, **context):
    response = render(request, "accounts/owner_mfa_policy.html", {
        "mfa_policy": policy, "mode": mode, **context,
    }, status=status)
    response["Referrer-Policy"] = "same-origin"
    return response


def reviewed_data(request, token, owner):
    saved = request.session.get(REVIEW_KEY, "")
    if not isinstance(saved, str) or not constant_time_compare(token, saved):
        raise signing.BadSignature
    data = signing.loads(token, salt=REVIEW_SALT, max_age=REVIEW_SECONDS)
    if (not isinstance(data, dict)
            or set(data) != {"actor", "org", "scope", "require_mfa", "version", "nonce"}
            or data["actor"] != owner.pk or data["org"] != str(owner.organization_id)
            or data["scope"] != "installation"
            or type(data["require_mfa"]) is not bool
            or type(data["version"]) is not int or data["version"] < 1):
        raise signing.BadSignature
    return data


@require_http_methods(["GET", "POST"])
@never_cache
@csrf_protect
@sensitive_post_parameters("password")
@sensitive_variables()
@login_required(login_url="two_factor:login")
def settings_view(request):
    if not mfa_policy.local_controls_enabled():
        raise Http404
    owner = mfa_policy.installation_owner(request.user)
    try:
        policy = mfa_policy.read_policy()
    except (ValidationError, DatabaseError):
        return page(request, mode="unavailable", status=503,
                    error="Installation policy unavailable. Review migration status before using this control.")
    mfa_policy.require_policy_mfa(request.user, policy)
    if request.method == "GET":
        return page(request, policy=policy, mfa_selection_form=MfaPolicySelectionForm(initial={
            "require_mfa": policy.require_mfa, "expected_version": policy.version,
        }))
    action = request.POST.get("action")
    if action == "cancel":
        request.session.pop(REVIEW_KEY, None)
        return redirect("owner-accounts:instructors")
    if action == "review":
        request.session.pop(REVIEW_KEY, None)
        form = MfaPolicySelectionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["expected_version"] != policy.version:
                form.add_error(None, "Policy changed. Reload before reviewing.")
            elif form.cleaned_data["require_mfa"] == policy.require_mfa:
                form.add_error(None, "Choose a different policy before reviewing.")
            else:
                desired = form.cleaned_data["require_mfa"]
                token = signing.dumps({
                    "actor": owner.pk, "org": str(owner.organization_id), "scope": "installation",
                    "require_mfa": desired, "version": policy.version, "nonce": secrets.token_hex(16),
                }, salt=REVIEW_SALT)
                request.session[REVIEW_KEY] = token
                return page(request, policy=policy, mode="review", desired_required=desired,
                            mfa_confirm_form=MfaPolicyConfirmationForm(initial={"token": token}))
        return page(request, policy=policy, status=400, mfa_selection_form=form)
    if action == "confirm":
        form = MfaPolicyConfirmationForm(request.POST)
        if form.is_valid():
            try:
                data = reviewed_data(request, form.cleaned_data["token"], owner)
                mfa_policy.change_policy(
                    actor=request.user, require_mfa=data["require_mfa"],
                    expected_version=data["version"], password=form.cleaned_data["password"],
                    confirmed=form.cleaned_data["confirm"],
                )
            except (signing.BadSignature, ValidationError):
                request.session.pop(REVIEW_KEY, None)
                return page(request, policy=policy, mode="review-error", status=400,
                            error="Unable to save. Check the current password and reload/review the policy again.")
            request.session.pop(REVIEW_KEY, None)
            messages.success(request, "Global MFA policy saved.")
            return redirect("owner-accounts:mfa-policy")
        return page(request, policy=policy, mode="confirm-error", status=400, mfa_confirm_form=form)
    request.session.pop(REVIEW_KEY, None)
    return page(request, policy=policy, mode="review-error", status=400,
                error="Select, review and explicitly confirm the installation-wide change.")
