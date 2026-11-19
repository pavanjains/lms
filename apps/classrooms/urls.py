from django.urls import path

from apps.classrooms import credential_views, student_views, views

app_name = "classrooms"
urlpatterns = [
    path("", views.classroom_list, name="list"),
    path("new/", views.classroom_create, name="create"),
    path("<int:classroom_id>/", views.classroom_detail, name="detail"),
    path("<int:classroom_id>/students/new/", student_views.student_create, name="create-student"),
    path("<int:classroom_id>/students/<int:student_id>/credentials/",
         credential_views.student_credentials, name="student-credentials"),
    path("<int:classroom_id>/<str:operation>/", views.classroom_action, name="action"),
]
