from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import F
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.policies import staff_mfa_required
from apps.classrooms import services
from apps.classrooms.forms import ClassroomForm, ConfirmationForm, TargetForm
from apps.classrooms.policies import (
    current_staff, visible_classrooms, visible_class_students, visible_students,
)
from apps.lessons.assignments import staff_assignments


OPERATIONS = {
    "archive": ("Archive class", services.archive_classroom, None),
    "assign-instructor": ("Assign instructor", services.assign_instructor, "instructor_id"),
    "remove-instructor": ("Remove instructor", services.remove_instructor, "instructor_id"),
    "enroll-student": ("Enroll student", services.enroll_student, "student_id"),
    "end-enrollment": ("End enrollment", services.end_enrollment, "student_id"),
}


def page(request, template, context, status=200):
    response = render(request, "classrooms/" + template, context, status=status)
    response["Referrer-Policy"] = "same-origin"
    return response


def owner_required(user):
    if user.role != "OWNER":
        raise PermissionDenied


@require_safe
@staff_mfa_required
def classroom_list(request):
    user = current_staff(request.user)
    rooms = visible_classrooms(request.user).order_by("name", "pk")
    return page(request, "list.html", {
        "rooms": Paginator(rooms, 20).get_page(request.GET.get("page")),
        "is_owner": user.role == "OWNER",
    })


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def classroom_create(request):
    owner_required(current_staff(request.user))
    form = ClassroomForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            room = services.create_classroom(
                actor=request.user, name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to create class. Check the name or reload and retry.")
        else:
            messages.success(request, "Class created.")
            return redirect("classrooms:detail", classroom_id=room.pk)
    return page(request, "form.html", {"title": "Create class", "form": form},
                400 if request.method == "POST" else 200)


@require_safe
@staff_mfa_required
def classroom_detail(request, classroom_id):
    user = current_staff(request.user)
    room = get_object_or_404(visible_classrooms(request.user), pk=classroom_id)
    students = None
    instructors = []
    if room.is_active:
        roster = visible_class_students(request.user, room.pk).annotate(
            grade=F("student_profile__grade"),
        ).values("pk", "username", "display_name", "grade", "is_staff", "is_superuser").order_by("username", "pk")
        students = Paginator(roster, 20).get_page(request.GET.get("page"))
        instructors = list(get_user_model().objects.filter(
            organization_id=user.organization_id, role="INSTRUCTOR",
            classroom_memberships__classroom=room, classroom_memberships__is_active=True,
        ).values("username", "display_name", "is_active").order_by("username"))
    assignments = staff_assignments(request.user).filter(classroom=room).select_related("student")
    return page(request, "detail.html", {
        "room": room, "students": students, "instructors": instructors,
        "assignments": Paginator(assignments, 20).get_page(request.GET.get("assignments_page")),
        "is_owner": user.role == "OWNER",
    })


def target_choices(actor, user, room, operation):
    accounts = get_user_model().objects.filter(organization_id=user.organization_id)
    if operation == "assign-instructor":
        accounts = accounts.filter(role="INSTRUCTOR", is_active=True)
    elif operation == "remove-instructor":
        accounts = accounts.filter(role="INSTRUCTOR", classroom_memberships__classroom=room,
                                   classroom_memberships__is_active=True)
    elif operation == "enroll-student":
        accounts = visible_students(actor)
    else:
        accounts = accounts.filter(role="STUDENT", classroom_enrollments__classroom=room,
                                   classroom_enrollments__is_active=True)
    return list(accounts.order_by("username", "pk").values_list("pk", "username").distinct())


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def classroom_action(request, classroom_id, operation):
    if operation not in OPERATIONS:
        raise Http404
    user = current_staff(request.user)
    if operation in {"archive", "assign-instructor", "remove-instructor"}:
        owner_required(user)
    room = get_object_or_404(visible_classrooms(request.user), pk=classroom_id)
    if not room.is_active and operation != "archive":
        raise Http404
    title, service, target_field = OPERATIONS[operation]
    data = request.POST if request.method == "POST" else None
    form = (TargetForm(data, choices=target_choices(request.user, user, room, operation))
            if target_field else ConfirmationForm(data))
    if request.method == "POST" and form.is_valid():
        arguments = {"actor": request.user, "classroom_id": room.pk}
        if target_field:
            arguments[target_field] = form.cleaned_data["target"]
        try:
            service(**arguments)
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to save. Reload the page and check the selected account.")
        else:
            messages.success(request, title + ": saved.")
            return redirect("classrooms:detail", classroom_id=room.pk)
    return page(request, "form.html", {
        "title": title, "room": room, "form": form, "archiving": operation == "archive",
    }, 400 if request.method == "POST" else 200)
