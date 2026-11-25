from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe


@require_safe
def home(request):
    from apps.accounts import students

    user = request.user
    workspace_url = None
    if user.is_authenticated:
        role = getattr(user, "role", "")
        workspace_url = reverse("student-home" if role == "STUDENT" else "staff-home")
    return render(request, "core/home.html", {
        "staff_login_enabled": bool(getattr(settings, "LMS_STAFF_AUTH_ENABLED", False)),
        "student_login_enabled": students.enabled(),
        "workspace_url": workspace_url,
    })


@require_safe
def liveness(request):
    return JsonResponse({"status": "ok"})
