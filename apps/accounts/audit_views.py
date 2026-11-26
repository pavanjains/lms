from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from apps.accounts import audit
from apps.accounts.audit_models import AuditEvent, AuditEventType
from apps.accounts.owner_views import require_owner
from apps.accounts.policies import staff_mfa_required

PAGE_SIZE = 50


@require_safe
@never_cache
@staff_mfa_required
def audit_log(request):
    require_owner(request.user)
    labels = dict(AuditEventType.choices)
    selected = request.GET.get("type", "")
    events = AuditEvent.objects.filter(organization_id=request.user.organization_id)
    if selected in labels:
        events = events.filter(event_type=selected)
    else:
        selected = ""
    page = Paginator(events.order_by("-created_at", "-pk"), PAGE_SIZE).get_page(request.GET.get("page"))
    for event in page:
        event.label = labels.get(event.event_type, event.event_type)
    return render(request, "accounts/owner_audit.html", {
        "page": page, "selected": selected, "types": AuditEventType.choices,
        "retention_days": audit.retention_days(),
    })
