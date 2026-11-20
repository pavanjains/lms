import secrets

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import constant_time_compare
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from apps.accounts.policies import staff_mfa_required
from apps.classrooms.policies import current_staff, visible_class_students, visible_classrooms
from apps.lessons.assignments import (
    GRADE_NUMBERS, cancel_assignment, create_assignments, staff_assignments,
)
from apps.lessons.models import Lesson, LessonAssignment, validate_lego_url

REVIEW_KEY = "assignment_review_token"
REVIEW_SALT = "lessons.assignment-review.v1"
REVIEW_SECONDS = 900


class SelectionForm(forms.Form):
    lesson = forms.ModelChoiceField(queryset=Lesson.objects.none())
    students = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, actor, room, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room
        self.fields["lesson"].queryset = Lesson.objects.filter(
            organization_id=room.organization_id, is_active=True,
        ).order_by("title", "pk")
        self.fields["students"].queryset = visible_class_students(actor, room.pk).filter(
            is_staff=False, is_superuser=False,
        ).select_related("student_profile").order_by("display_name", "username", "pk")

    def clean_students(self):
        raw = self.data.getlist("students")
        if len(raw) != len(set(raw)):
            raise forms.ValidationError("Select each student only once.")
        return self.cleaned_data["students"]

    def clean(self):
        data = super().clean()
        lesson, students = data.get("lesson"), data.get("students")
        if lesson is not None and students:
            try:
                lesson.full_clean()
            except ValidationError:
                raise forms.ValidationError("The selected lesson is invalid. Ask its creator to review it.") from None
            for student in students:
                grade = GRADE_NUMBERS.get(student.student_profile.grade)
                if grade is None or not lesson.min_grade <= grade <= lesson.max_grade:
                    raise forms.ValidationError("All selected students must match the lesson grade/kit range.")
            if LessonAssignment.objects.filter(
                classroom=self.room, lesson=lesson, student__in=students, cancelled_at__isnull=True,
            ).exists():
                raise forms.ValidationError("A selected student already has this active assignment.")
        return data


class ReviewForm(forms.Form):
    token = forms.CharField(max_length=4096, widget=forms.HiddenInput)
    confirm = forms.BooleanField(label="Assign this reviewed lesson to these students")


class CancelForm(forms.Form):
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    confirm = forms.BooleanField(label="Cancel this assignment and retain its history")


def page(request, mode, *, status=200, **context):
    content = context.get("content")
    if content:
        try:
            context["external_url"] = validate_lego_url(content.lego_url)
        except ValidationError:
            context["external_url"] = None
    response = render(request, "lessons/assignments.html", {"mode": mode, **context}, status=status)
    response["Referrer-Policy"] = "same-origin"
    return response


@require_safe
@staff_mfa_required
def assignment_list(request):
    rows = staff_assignments(request.user).select_related("classroom", "student")
    return page(request, "list", rooms=visible_classrooms(request.user).filter(is_active=True),
                assignments=Paginator(rows, 20).get_page(request.GET.get("page")))


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def assignment_create(request, classroom_id):
    user = current_staff(request.user)
    room = get_object_or_404(visible_classrooms(request.user), pk=classroom_id, is_active=True)
    if request.method == "POST" and request.POST.get("action") == "confirm":
        form = ReviewForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data["token"]
            try:
                if not constant_time_compare(token, request.session.get(REVIEW_KEY, "")):
                    raise signing.BadSignature
                data = signing.loads(token, salt=REVIEW_SALT, max_age=REVIEW_SECONDS)
                if (data["actor"] != user.pk or data["org"] != user.organization_id
                        or data["room"] != room.pk):
                    raise PermissionDenied
                rows = create_assignments(
                    actor=request.user, classroom_id=room.pk, lesson_id=data["lesson"],
                    student_ids=data["students"], expected_lesson_version=data["version"],
                )
            except (signing.BadSignature, ValidationError, IntegrityError):
                request.session.pop(REVIEW_KEY, None)
                form.add_error(None, "Review expired or data changed. Select and review again.")
            else:
                request.session.pop(REVIEW_KEY, None)
                messages.success(request, f"Created {len(rows)} student assignment(s).")
                return redirect("lessons:assignment-list")
        return page(request, "review-error", status=400, form=form, room=room)
    if request.method == "POST" and request.POST.get("action") != "review":
        return page(request, "review-error", status=400, room=room,
                    error="Select a lesson and students, then review before confirming.")
    form = SelectionForm(request.POST if request.method == "POST" else None,
                         actor=request.user, room=room)
    if request.method == "POST":
        request.session.pop(REVIEW_KEY, None)
        if form.is_valid():
            lesson = form.cleaned_data["lesson"]
            recipients = list(form.cleaned_data["students"])
            token = signing.dumps({
                "actor": user.pk, "org": user.organization_id, "room": room.pk,
                "lesson": lesson.pk, "version": lesson.version,
                "students": [student.pk for student in recipients], "nonce": secrets.token_hex(16),
            }, salt=REVIEW_SALT)
            request.session[REVIEW_KEY] = token
            return page(request, "review", room=room, content=lesson, recipients=recipients,
                        source_version=lesson.version, form=ReviewForm(initial={"token": token}))
    return page(request, "select", status=400 if request.method == "POST" else 200,
                form=form, room=room)


def detail_page(request, row, form=None, status=200):
    user = current_staff(request.user)
    return page(request, "detail", status=status, row=row, content=row,
                source_version=row.lesson_version,
                can_cancel=row.cancelled_at is None and (row.classroom.is_active or user.role == "OWNER"),
                form=form if form is not None else CancelForm(initial={"expected_version": row.version}))


@require_safe
@staff_mfa_required
def assignment_detail(request, assignment_id):
    row = get_object_or_404(staff_assignments(request.user).select_related("classroom", "student"),
                            pk=assignment_id)
    return detail_page(request, row)


@require_POST
@staff_mfa_required
def assignment_cancel(request, assignment_id):
    row = get_object_or_404(staff_assignments(request.user).select_related("classroom", "student"),
                            pk=assignment_id)
    form = CancelForm(request.POST)
    if form.is_valid():
        try:
            cancel_assignment(actor=request.user, assignment_id=row.pk,
                              expected_version=form.cleaned_data["expected_version"])
        except (ValidationError, IntegrityError):
            form.add_error(None, "Assignment changed. Reload before cancelling.")
        else:
            messages.success(request, "Assignment cancelled; history retained.")
            return redirect("lessons:assignment-detail", assignment_id=row.pk)
    return detail_page(request, row, form=form, status=400)
