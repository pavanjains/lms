from django import template

from apps.accounts.mfa_policy_views import selection_context

register = template.Library()


@register.inclusion_tag("accounts/_mfa_policy_selection.html", takes_context=True)
def mfa_policy_panel(context):
    request = context.get("request")
    data = selection_context(request.user) if request is not None else {}
    data["csrf_token"] = context.get("csrf_token")
    return data
