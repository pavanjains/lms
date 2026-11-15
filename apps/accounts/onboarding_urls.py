from django.urls import path

from apps.accounts.onboarding import activate, complete

app_name = "onboarding"
urlpatterns = [
    path("activate/<str:token>/", activate, name="activate"),
    path("complete/", complete, name="complete"),
]
