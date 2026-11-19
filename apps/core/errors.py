from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def csrf_failure(request, reason=""):
    return render(request, "403.html", status=403)
