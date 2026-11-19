from django.urls import path

from apps.documents import views as document_views
from apps.lessons import views

app_name = "lessons"
urlpatterns = [
    path("", views.library, name="list"),
    path("new/", views.edit, name="create"),
    path("<int:lesson_id>/", views.detail, name="detail"),
    path("<int:lesson_id>/edit/", views.edit, name="edit"),
    path("<int:lesson_id>/archive/", views.archive, name="archive"),
    path("<int:lesson_id>/documents/", document_views.document_list, name="documents"),
    path("<int:lesson_id>/documents/new/", document_views.upload, name="upload-document"),
    path("<int:lesson_id>/documents/<int:document_id>/download/", document_views.download, name="download-document"),
    path("<int:lesson_id>/documents/<int:document_id>/archive/", document_views.archive, name="archive-document"),
]
