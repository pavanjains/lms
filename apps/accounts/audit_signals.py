from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in, dispatch_uid="accounts_audit_sign_in")
def record_completed_sign_in(sender, request, user, **kwargs):
    from apps.accounts import audit

    audit.record_sign_in(user)
