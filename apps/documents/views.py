import hashlib
from io import BytesIO

from django import forms
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.policies import staff_mfa_required
from apps.classrooms.forms import ConfirmationForm
from apps.classrooms.policies import current_staff
from apps.documents.models import LessonDocument
from apps.documents.services import archive_document, enabled, upload_document
from apps.lessons.services import can_manage, visible_lessons


class DocumentForm(ConfirmationForm):
    title = forms.CharField(max_length=200)
    file = forms.FileField(label="PDF (maximum 5 MiB)",
                           widget=forms.ClearableFileInput(attrs={"accept": ".pdf,application/pdf"}))
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class ArchiveForm(ConfirmationForm):
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


def lesson_for(request, lesson_id):
    enabled()
    return get_object_or_404(visible_lessons(request.user), pk=lesson_id)


def page(request, context, status=200):
    response = render(request, "documents/manage.html", context, status=status)
    response["Referrer-Policy"] = "same-origin"
    return response


@require_safe
@staff_mfa_required
def document_list(request, lesson_id):
    lesson = lesson_for(request, lesson_id)
    documents = list(LessonDocument.objects.filter(lesson=lesson, is_active=True).values(
        "pk", "title", "original_name", "size",
    ).order_by("title", "pk"))
    return page(request, {"lesson": lesson, "documents": documents,
                           "can_manage": lesson.is_active and can_manage(current_staff(request.user), lesson)})


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def upload(request, lesson_id):
    lesson = lesson_for(request, lesson_id)
    if not lesson.is_active or not can_manage(current_staff(request.user), lesson):
        raise PermissionDenied
    form = DocumentForm(request.POST if request.method == "POST" else None,
                        request.FILES if request.method == "POST" else None,
                        initial={"expected_version": lesson.version})
    if request.method == "POST" and form.is_valid():
        try:
            upload_document(actor=request.user, lesson_id=lesson.pk,
                            expected_version=form.cleaned_data["expected_version"],
                            title=form.cleaned_data["title"], upload=form.cleaned_data["file"])
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to upload. Check PDF/size/quota or reload the lesson before retrying.")
        else:
            return redirect("lessons:documents", lesson_id=lesson.pk)
    return page(request, {"lesson": lesson, "form": form, "uploading": True},
                400 if request.method == "POST" else 200)


@require_safe
@staff_mfa_required
def download(request, lesson_id, document_id):
    lesson = lesson_for(request, lesson_id)
    document = get_object_or_404(LessonDocument, pk=document_id, lesson=lesson, is_active=True)
    payload = bytes(document.content)
    if len(payload) != document.size or hashlib.sha256(payload).hexdigest() != document.checksum:
        raise Http404
    response = FileResponse(BytesIO(payload), as_attachment=True,
                            filename=f"lesson-{lesson.pk}-document-{document.pk}.pdf",
                            content_type="application/octet-stream")
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = "default-src 'none'; sandbox"
    response["X-Robots-Tag"] = "noindex, noarchive"
    return response


@require_http_methods(["GET", "POST"])
@staff_mfa_required
def archive(request, lesson_id, document_id):
    lesson = lesson_for(request, lesson_id)
    if not lesson.is_active or not can_manage(current_staff(request.user), lesson):
        raise PermissionDenied
    document = get_object_or_404(LessonDocument.objects.defer("content"),
                                 pk=document_id, lesson=lesson, is_active=True)
    form = ArchiveForm(request.POST if request.method == "POST" else None,
                       initial={"expected_version": lesson.version})
    if request.method == "POST" and form.is_valid():
        try:
            archive_document(actor=request.user, lesson_id=lesson.pk, document_id=document.pk,
                             expected_version=form.cleaned_data["expected_version"])
        except (ValidationError, IntegrityError):
            form.add_error(None, "Unable to archive. Reload before retrying.")
        else:
            return redirect("lessons:documents", lesson_id=lesson.pk)
    return page(request, {"lesson": lesson, "document": document, "form": form},
                400 if request.method == "POST" else 200)
