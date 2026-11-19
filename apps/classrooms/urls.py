from django.urls import path

from apps.classrooms import views

app_name = "classrooms"
urlpatterns = [
    path("", views.classroom_list, name="list"),
    path("new/", views.classroom_create, name="create"),
    path("<int:classroom_id>/", views.classroom_detail, name="detail"),
    path("<int:classroom_id>/<str:operation>/", views.classroom_action, name="action"),
]
