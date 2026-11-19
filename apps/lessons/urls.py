from django.urls import path

from apps.lessons import views

app_name = "lessons"
urlpatterns = [
    path("", views.library, name="list"),
    path("new/", views.edit, name="create"),
    path("<int:lesson_id>/", views.detail, name="detail"),
    path("<int:lesson_id>/edit/", views.edit, name="edit"),
    path("<int:lesson_id>/archive/", views.archive, name="archive"),
]
