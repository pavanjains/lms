from django.urls import path

from apps.documents import views as document_views
from apps.lessons import assignment_views, views

app_name = "lessons"
urlpatterns = [
    path("", views.library, name="list"),
    path("new/", views.edit, name="create"),
    path("assignments/", assignment_views.assignment_list, name="assignment-list"),
    path("assignments/classes/<int:classroom_id>/new/", assignment_views.assignment_create, name="assignment-create"),
    path("assignments/<int:assignment_id>/", assignment_views.assignment_detail, name="assignment-detail"),
    path("assignments/<int:assignment_id>/cancel/", assignment_views.assignment_cancel, name="assignment-cancel"),
    path("assignments/<int:assignment_id>/progress/", assignment_views.assignment_progress, name="assignment-progress"),
    path("<int:lesson_id>/", views.detail, name="detail"),
    path("<int:lesson_id>/edit/", views.edit, name="edit"),
    path("<int:lesson_id>/archive/", views.archive, name="archive"),
    path("<int:lesson_id>/documents/", document_views.document_list, name="documents"),
    path("<int:lesson_id>/documents/new/", document_views.upload, name="upload-document"),
    path("<int:lesson_id>/documents/<int:document_id>/download/", document_views.download, name="download-document"),
    path("<int:lesson_id>/documents/<int:document_id>/archive/", document_views.archive, name="archive-document"),
]
