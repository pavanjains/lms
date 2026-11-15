import getpass
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from apps.organizations.models import Organization


class Command(BaseCommand):
    help = "Create the initial organization and LMS owner; never modify existing accounts."

    def add_arguments(self, parser):
        parser.add_argument("--organization", required=True)
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--noinput", action="store_true")

    def handle(self, *args, **options):
        name = options["organization"].strip()
        username = options["username"].strip()
        email = options["email"].strip().lower()
        if not all((name, username, email)):
            raise CommandError("Organization, username, and email must not be empty.")
        try:
            with transaction.atomic():
                self._bootstrap(name, username, email, options["noinput"])
        except ValidationError as exc:
            raise CommandError("; ".join(exc.messages)) from None
        except IntegrityError:
            raise CommandError(
                "Initialization conflicted with existing data. No changes were saved. "
                "Check the organization and account identifiers before retrying."
            ) from None

    def _bootstrap(self, name, username, email, noinput):
        User = get_user_model()
        organizations = list(Organization.objects.select_for_update().all()[:2])
        if organizations:
            organization = organizations[0]
            existing = User.objects.filter(username=username).first()
            matches = (
                len(organizations) == 1
                and organization.name == name
                and organization.is_active
                and existing is not None
                and existing.organization_id == organization.pk
                and existing.role == User.Role.OWNER
                and existing.is_active
                and existing.email.casefold() == email.casefold()
            )
            if matches:
                self.stdout.write("Owner already initialized; no changes made.")
                return
            raise CommandError(
                "Installation already contains organization data. "
                "Bootstrap will not create another organization or alter existing accounts."
            )
        if User.objects.filter(username=username).exists():
            raise CommandError("Username is already in use; no changes made.")
        password = os.environ.get("LMS_BOOTSTRAP_PASSWORD")
        if not password:
            if noinput:
                raise CommandError("Set LMS_BOOTSTRAP_PASSWORD for noninteractive initialization.")
            password = getpass.getpass("Owner password: ")
            if password != getpass.getpass("Confirm owner password: "):
                raise CommandError("Passwords do not match; no changes made.")
        organization = Organization(name=name)
        organization.full_clean()
        organization.save()
        owner = User(
            organization=organization,
            username=username,
            email=email,
            role=User.Role.OWNER,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        validate_password(password, user=owner)
        owner.set_password(password)
        owner.full_clean()
        owner.save()
        self.stdout.write(self.style.SUCCESS(
            "Initial owner created. Staff login and MFA must be implemented before use."
        ))
