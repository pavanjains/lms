from django.urls import path

from apps.core.views import home, liveness

urlpatterns = [
    path("", home, name="home"),
    path("health/live/", liveness, name="liveness"),
]
