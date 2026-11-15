from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.invitation_services import (
    accept_instructor_invitation, issue_instructor_invitation, revoke_instructor_invitation,
)
from apps.accounts.models import InstructorInvitation
from apps.organizations.models import Organization


class InstructorInvitationTests(TestCase):
    password = "Synthetic-Invitation-Password!72391"

    def setUp(self):
        User = get_user_model()
        self.organization = Organization.objects.create(name="Synthetic Center")
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.test", role="OWNER",
            organization=self.organization,
        )
        self.verification = patch.object(self.owner, "is_verified", return_value=True, create=True)
        self.verification.start()
        self.addCleanup(self.verification.stop)

    def issue(self, email="new@example.test"):
        return issue_instructor_invitation(actor=self.owner, email=email)

    def accept(self, token, **options):
        return accept_instructor_invitation(
            token=token, username=options.get("username", "new-instructor"),
            password=options.get("password", self.password),
        )

    def test_stores_only_digest_and_normalizes_email(self):
        invitation, token = self.issue(" New@Example.test ")
        self.assertEqual(invitation.email, "new@example.test")
        self.assertNotEqual(invitation.token_digest, token)
        self.assertEqual(len(invitation.token_digest), 64)
        self.assertNotIn(token, str(invitation.__dict__))

    def test_accept_creates_only_instructor_and_records_acceptance(self):
        invitation, token = self.issue()
        user = self.accept(token)
        invitation.refresh_from_db()
        self.assertEqual(user.role, "INSTRUCTOR")
        self.assertEqual(user.organization_id, self.organization.pk)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(invitation.accepted_user_id, user.pk)
        self.assertIsNotNone(invitation.accepted_at)

    def test_token_is_one_time(self):
        _, token = self.issue()
        self.accept(token)
        with self.assertRaises(ValidationError):
            self.accept(token, username="another")

    def test_reissue_revokes_previous_token(self):
        old, old_token = self.issue()
        _, new_token = self.issue()
        old.refresh_from_db()
        self.assertIsNotNone(old.revoked_at)
        with self.assertRaises(ValidationError):
            self.accept(old_token)
        self.accept(new_token)

    def test_revoked_invitation_cannot_be_accepted(self):
        invitation, token = self.issue()
        revoke_instructor_invitation(actor=self.owner, invitation_id=invitation.pk)
        with self.assertRaises(ValidationError):
            self.accept(token)

    def test_expired_invitation_cannot_be_accepted(self):
        invitation, token = self.issue()
        invitation.expires_at = timezone.now() - timedelta(seconds=1)
        invitation.save(update_fields=["expires_at"])
        with self.assertRaises(ValidationError):
            self.accept(token)

    def test_unknown_token_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.accept("not-a-real-invitation-token")

    def test_unverified_owner_cannot_issue(self):
        with patch.object(self.owner, "is_verified", return_value=False):
            with self.assertRaises(PermissionDenied):
                self.issue()

    def test_instructor_cannot_issue(self):
        self.owner.role = "INSTRUCTOR"
        with self.assertRaises(PermissionDenied):
            self.issue()

    def test_disabled_owner_invalidates_pending_invitation(self):
        _, token = self.issue()
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            self.accept(token)

    def test_disabled_organization_invalidates_invitation(self):
        _, token = self.issue()
        self.organization.is_active = False
        self.organization.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            self.accept(token)

    def test_cross_organization_revoke_is_denied(self):
        other = Organization.objects.create(name="Other Center")
        invitation, _ = self.issue()
        invitation.organization = other
        invitation.save(update_fields=["organization"])
        with self.assertRaises(PermissionDenied):
            revoke_instructor_invitation(actor=self.owner, invitation_id=invitation.pk)

    def test_existing_staff_email_cannot_be_invited(self):
        with self.assertRaises(ValidationError):
            self.issue(self.owner.email.upper())

    def test_username_collision_does_not_consume_invitation(self):
        invitation, token = self.issue()
        with self.assertRaises(ValidationError):
            self.accept(token, username=self.owner.username)
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_at)
        self.accept(token)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 18},
    }])
    def test_weak_password_does_not_consume_invitation(self):
        invitation, token = self.issue()
        with self.assertRaises(ValidationError):
            self.accept(token, password="short")
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_at)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_invalid_email_creates_no_invitation(self):
        with self.assertRaises(ValidationError):
            self.issue("not-an-email")
        self.assertFalse(InstructorInvitation.objects.exists())

    def test_accepted_invitation_cannot_be_revoked(self):
        invitation, token = self.issue()
        self.accept(token)
        with self.assertRaises(ValidationError):
            revoke_instructor_invitation(actor=self.owner, invitation_id=invitation.pk)
