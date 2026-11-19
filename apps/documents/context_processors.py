from django.conf import settings


def document_features(request):
    return {"lesson_documents_enabled": getattr(settings, "LMS_LESSON_DOCUMENTS_ENABLED", False)}
