import math
import time

from django import forms
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, authenticate, get_user_model, login, logout
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.cache import patch_cache_control
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from apps.accounts import throttle
from apps.classrooms.models import Classroom
from apps.organizations.models import Organization

STUDENT_BACKEND = "apps.accounts.students.StudentBackend"
STARTED = "student_started_at"
SEEN = "student_last_seen"


def enabled():
    return (getattr(settings, "LMS_STUDENT_AUTH_ENABLED", False)
            and settings.SESSION_ENGINE == "django.contrib.sessions.backends.db")


def limits():
    idle = int(getattr(settings, "LMS_STUDENT_IDLE_SECONDS", 900))
    absolute = int(getattr(settings, "LMS_STUDENT_ABSOLUTE_SECONDS", 14400))
    if not 1 <= idle <= absolute <= 86400:
        raise ImproperlyConfigured("Invalid student session limits.")
    return idle, absolute


def students():
    return get_user_model().objects.filter(
        role="STUDENT", is_active=True, is_staff=False, is_superuser=False,
        organization__is_active=True, student_profile__isnull=False,
    )


class StudentBackend(BaseBackend):
    @sensitive_variables()
    def authenticate(self, request, student_username=None, password=None, **kwargs):
        if not enabled() or not isinstance(student_username, str) or not isinstance(password, str):
            return None
        if not student_username.strip() or len(student_username) > 150 or not 1 <= len(password) <= 128:
            return None
        User = get_user_model()
        candidate = students().filter(
            username=User.normalize_username(student_username.strip()),
        ).values("pk", "organization_id").first()
        if candidate is None:
            User().set_password(password)
            return None
        with transaction.atomic():
            org = Organization.objects.select_for_update().filter(
                pk=candidate["organization_id"], is_active=True,
            ).first()
            user = students().select_for_update(of=("self",)).filter(
                pk=candidate["pk"], organization=org,
            ).first() if org else None
            if user is not None and user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        if not enabled():
            return None
        return students().filter(pk=user_id).first()


class StudentSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.session.get(BACKEND_SESSION_KEY) != STUDENT_BACKEND:
            return
        if not request.user.is_authenticated:
            logout(request)
            return
        now = time.time()
        started, seen = request.session.get(STARTED), request.session.get(SEEN)
        idle, absolute = limits()
        valid = all(isinstance(value, (int, float)) and math.isfinite(value)
                    for value in (started, seen))
        if (not valid or not started <= seen <= now
                or now - seen >= idle or now - started >= absolute):
            logout(request)
            return
        if request.path_info.startswith("/students/"):
            request.session[SEEN] = now
            request.session.set_expiry(max(1, int(min(idle, absolute - (now - started)))))

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.path_info.startswith("/students/"):
            return None
        if not enabled():
            raise Http404
        if request.resolver_match.url_name == "student-login":
            return None
        if not request.user.is_authenticated:
            return redirect("student-login")
        if request.session.get(BACKEND_SESSION_KEY) != STUDENT_BACKEND:
            raise PermissionDenied
        return None

    def process_response(self, request, response):
        if request.path_info.startswith("/students/"):
            patch_cache_control(response, private=True, no_store=True, no_cache=True,
                                max_age=0, must_revalidate=True)
            response["Referrer-Policy"] = "same-origin"
        return response


class StudentLoginForm(forms.Form):
    student_username = forms.CharField(max_length=150, label="Username",
                                       widget=forms.TextInput(attrs={"autocomplete": "username"}))
    password = forms.CharField(max_length=128, strip=False,
                                widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))


@require_http_methods(["GET", "POST"])
@sensitive_post_parameters()
@sensitive_variables()
def sign_in(request):
    if request.user.is_authenticated:
        if (request.method == "GET"
                and request.session.get(BACKEND_SESSION_KEY) == STUDENT_BACKEND):
            return redirect("student-home")
        return render(request, "students/login.html", {"conflict": True}, status=409)
    idle, _ = limits()
    form = StudentLoginForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        submitted_name = form.cleaned_data["student_username"]
        if throttle.is_locked(throttle.STUDENT, submitted_name):
            form.add_error(None, throttle.LOCKED_MESSAGE)
            return render(request, "students/login.html", {"form": form}, status=429)
        with transaction.atomic():
            user = authenticate(request, **form.cleaned_data)
            if user is not None:
                request.session.flush()
                login(request, user, backend=STUDENT_BACKEND)
                now = time.time()
                request.session[STARTED] = now
                request.session[SEEN] = now
                request.session.set_expiry(idle)
                request.session.save()
        if user is not None:
            throttle.reset(throttle.STUDENT, submitted_name)
            return redirect("student-home")
        throttle.record_failure(throttle.STUDENT, submitted_name)
        form.add_error(None, "Unable to sign in. Check your username and password.")
    return render(request, "students/login.html", {"form": form},
                  status=400 if request.method == "POST" else 200)


@require_safe
def home(request):
    user = request.user
    rooms = list(Classroom.objects.filter(
        organization_id=user.organization_id, is_active=True,
        enrollment_links__student_id=user.pk, enrollment_links__is_active=True,
    ).values_list("name", flat=True).order_by("name").distinct())
    return render(request, "students/home.html", {
        "display_name": user.display_name or user.username,
        "grade": user.student_profile.grade, "class_names": rooms,
    })


@require_POST
def sign_out(request):
    logout(request)
    return redirect("student-login")
