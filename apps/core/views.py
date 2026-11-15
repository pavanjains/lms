from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def home(request):
    return render(request, "core/home.html")


@require_safe
def liveness(request):
    return JsonResponse({"status": "ok"})
