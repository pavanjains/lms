from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.policies import staff_mfa_required
from apps.classrooms.policies import current_staff
from apps.lessons import services
from apps.lessons.forms import ArchiveForm, FilterForm, LessonForm
from apps.lessons.models import LESSON_FIELDS, validate_lego_url


def page(request, template, context, status=200):
    response = render(request, "lessons/" + template, context, status=status)
    response["Referrer-Policy"] = "same-origin"
    return response


@require_safe
@staff_mfa_required
def library(request):
    lessons = services.visible_lessons(request.user)
    form = FilterForm(request.GET if request.GET else {"status": "active"})
    valid = form.is_valid()
    if valid:
        data = form.cleaned_data
        if data["q"]:
            lessons = lessons.filter(Q(title__icontains=data["q"]) | Q(summary__icontains=data["q"]))
        if data["kit"]:
            lessons = lessons.filter(kit=data["kit"])
        if data["grade"] is not None:
            lessons = lessons.filter(min_grade__lte=data["grade"], max_grade__gte=data["grade"])
        status = data["status"] or "active"
        if status != "all":
            lessons = lessons.filter(is_active=status == "active")
    else:
        lessons = lessons.none()
    query = request.GET.copy()
    query.pop("page", None)
    return page(request, "list.html", {
        "form": form, "lessons": Paginator(lessons.order_by("title", "pk"), 20).get_page(request.GET.get("page")),
        "query": query.urlencode(),
    }, 200 if valid else 400)


@require_safe
@staff_mfa_required
def detail(request, lesson_id):
    lesson = get_object_or_404(services.visible_lessons(request.user), pk=lesson_id)
    try:
        external_url = validate_lego_url(lesson.lego_url)
    except ValidationError:
        external_url = None
    return page(request, "detail.html", {
        "lesson": lesson, "external_url": external_url,
        "can_manage": services.can_manage(current_staff(request.user), lesson),
    })


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def edit(request, lesson_id=None):
    user = current_staff(request.user)
    lesson = get_object_or_404(services.visible_lessons(request.user), pk=lesson_id) if lesson_id else None
    if lesson and (not services.can_manage(user, lesson) or not lesson.is_active):
        raise PermissionDenied
    form = LessonForm(request.POST if request.method == "POST" else None, instance=lesson)
    if request.method == "POST" and form.is_valid():
        details = {name: form.cleaned_data[name] for name in LESSON_FIELDS}
        try:
            if lesson:
                saved = services.update_lesson(actor=request.user, lesson_id=lesson.pk,
                                               expected_version=form.cleaned_data["expected_version"], **details)
            else:
                saved = services.create_lesson(actor=request.user, **details)
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to save. Check the fields or reload; the lesson may have changed.")
        else:
            messages.success(request, "Lesson saved.")
            return redirect("lessons:detail", lesson_id=saved.pk)
    return page(request, "form.html", {"form": form, "lesson": lesson,
                                         "title": "Edit lesson" if lesson else "Create lesson"},
                400 if request.method == "POST" else 200)


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def archive(request, lesson_id):
    lesson = get_object_or_404(services.visible_lessons(request.user), pk=lesson_id)
    if not services.can_manage(current_staff(request.user), lesson):
        raise PermissionDenied
    form = ArchiveForm(request.POST if request.method == "POST" else None,
                       initial={"expected_version": lesson.version})
    if request.method == "POST" and form.is_valid():
        try:
            services.archive_lesson(actor=request.user, lesson_id=lesson.pk,
                                    expected_version=form.cleaned_data["expected_version"])
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to archive. Reload before retrying.")
        else:
            messages.success(request, "Lesson archived; record retained.")
            return redirect("lessons:list")
    return page(request, "form.html", {"form": form, "lesson": lesson,
                                         "title": "Archive lesson"},
                400 if request.method == "POST" else 200)
