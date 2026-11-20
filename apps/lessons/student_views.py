from functools import wraps

from django.contrib.auth import BACKEND_SESSION_KEY
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from apps.accounts.students import STUDENT_BACKEND, enabled
from apps.lessons.assignments import student_assignments
from apps.lessons.models import validate_lego_url


def student_session_required(view):
    @wraps(view)
    def guarded(request, *args, **kwargs):
        if not enabled():
            raise Http404
        if not request.user.is_authenticated:
            return redirect("student-login")
        if request.session.get(BACKEND_SESSION_KEY) != STUDENT_BACKEND:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return never_cache(guarded)


@require_safe
@student_session_required
def assignment_list(request):
    rows = student_assignments(request.user).select_related("classroom")
    return render(request, "students/assignments.html", {
        "assignments": Paginator(rows, 20).get_page(request.GET.get("page")),
    })


@require_safe
@student_session_required
def assignment_detail(request, assignment_id):
    row = get_object_or_404(
        student_assignments(request.user).select_related("classroom"), pk=assignment_id,
    )
    try:
        external_url = validate_lego_url(row.lego_url)
    except ValidationError:
        external_url = None
    return render(request, "students/assignment_detail.html", {
        "assignment": row, "external_url": external_url,
    })
