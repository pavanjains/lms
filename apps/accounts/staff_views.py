from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_safe
from two_factor.utils import default_device
from two_factor.views import LoginView

from apps.accounts import mfa_policy
from apps.accounts.policies import staff_mfa_required


class StaffAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)


def _only_when_mfa_required(step_condition):
    def condition(wizard):
        return mfa_policy.effective_mfa_required() and step_condition(wizard)
    return condition


class StaffLoginView(LoginView):
    form_list = tuple(
        (step, StaffAuthenticationForm if step == "auth" else form)
        for step, form in LoginView.form_list
    )
    # Second-factor steps are skipped only while explicit local controls turn MFA off.
    condition_dict = {
        step: _only_when_mfa_required(condition)
        for step, condition in getattr(LoginView, "condition_dict", {}).items()
    }

    def get_success_url(self):
        # Fixed local destinations: no first-factor redirect to business data.
        if not mfa_policy.effective_mfa_required():
            return reverse("staff-entry")
        if not default_device(self.get_user()):
            return reverse("two_factor:setup")
        return reverse("staff-entry")


@require_safe
def staff_entry(request):
    if request.user.is_verified():
        return redirect("staff-home")
    if not default_device(request.user):
        return redirect("two_factor:setup")
    return redirect("two_factor:login")


@require_safe
@staff_mfa_required
def staff_home(request):
    return render(request, "accounts/staff_home.html")


def deny_mfa_disable(request):
    raise PermissionDenied("Staff MFA cannot be disabled through self-service.")
