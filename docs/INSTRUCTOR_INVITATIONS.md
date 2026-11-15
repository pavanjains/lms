# Instructor invitations — service slice

## Scope
Adds invitation persistence, migration, issue/reissue, revoke, and one-time acceptance services. Only a currently active owner with verified MFA can issue or revoke. Acceptance creates an INSTRUCTOR account in the invitation organization; no superuser or framework is_staff privileges are granted. Existing accounts are not promoted or overwritten.

Raw invitation tokens are generated using secrets.token_urlsafe(32); only a SHA-256 digest is persisted. The raw token is returned once to the future delivery layer. Do not log it. No emails are sent and no public routes or screens are added in this slice.

## Lifecycle decisions
- Proposed default expiry is 48 hours, configurable with LMS_INVITATION_HOURS (1–168).
- Reissuing for the same organization/email revokes unaccepted prior invitations.
- Expired, revoked, used, unknown, disabled-organization, and inactive/non-owner-issuer invitations cannot be accepted.
- Existing staff email blocks invitation creation, including inactive staff; use account administration rather than a new invitation for recovery.
- Accepting with invalid account details or weak password leaves the invitation unconsumed.
- Operations lock organization then invitation consistently. PostgreSQL concurrency tests remain required; SQLite tests do not establish locking behavior.
- First login for the new instructor still requires the existing authenticator enrollment flow. Classes are not assigned automatically.

## Verification
```sh
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test apps.accounts.test_invitations --settings=config.settings.test
# With PostgreSQL configuration exported:
DJANGO_SETTINGS_MODULE=config.settings.ci python manage.py test
```
Seventeen tests are authored. Syntax checked only in the authoring environment; runtime and migration-drift verification are pending. The previous workflow passed according to the owner; this new slice has not yet run in CI.

## Remaining work
Owner invite/list/revoke screens; safe activation form with password confirmation; configured email delivery and failure/retry policy; delivery URL using an approved origin; referrer protection and redaction of activation URLs; login/activation throttling; invitation audit history; PostgreSQL simultaneous acceptance tests; browser UAT. These are required before exposing invitation acceptance operationally.
