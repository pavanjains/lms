from django.core.management.base import BaseCommand

from apps.accounts import audit


class Command(BaseCommand):
    help = "Delete audit events older than LMS_AUDIT_RETENTION_DAYS (default 90 days)."

    def handle(self, *args, **options):
        days = audit.retention_days()
        deleted = audit.purge_expired()
        self.stdout.write(f"Deleted {deleted} audit event(s) older than {days} days.")
