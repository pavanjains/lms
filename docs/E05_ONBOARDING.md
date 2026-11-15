# E05 instructor onboarding — development preview

Implements E05-02 invite form, E05-03 configured-backend delivery, E05-04 activation, E05-05 confirmed resend. Runtime/CI PENDING. No migration or real invitation is executed by this source commit.

## Flow
Owner completes MFA, opens instructor management, selects Invite instructor, enters email and confirms. Backend creates a one-time invitation and submits plain-text mail. Recipient chooses username and matching passwords. Server fixes role to INSTRUCTOR and organization to the invitation. Activation does not authenticate the recipient; the completion page links to staff sign-in, where MFA enrollment is mandatory.

Resend targets the stored recipient, not a submitted email. Successful resend invalidates old pending links. GET pages do not consume invitations or send messages. Signed-in users must sign out before activating another account.

## Local preview
Development retains console email; it prints invitation links, so use synthetic accounts only and treat local output as sensitive. Export both LMS_STAFF_AUTH_ENABLED=true and LMS_INSTRUCTOR_ONBOARDING_ENABLED=true. LMS_PUBLIC_ORIGIN defaults to http://localhost:8000 in development; LMS_INVITATION_FROM_EMAIL defaults to noreply@example.test. Neither onboarding nor staff auth is enabled by this commit. Production has no onboarding enablement or real mail credentials added.

For staging/production, an operator must explicitly configure Django settings for the onboarding flag, approved HTTPS origin, validated sender, and mail backend/credentials. Origin is never derived from request Host. Only loopback HTTP is allowed with DEBUG=true. No inbox-delivery guarantee is made from a backend success result.

## Delivery failure policy
Issue/replacement and mail submission occur inside a database transaction. A synchronous SMTP/OS error or zero accepted messages rolls back new invitation and replacement revocations; retry uses a fresh token. Do not automatically retry after ambiguous delivery. Mail and database are not a distributed transaction: provider acceptance followed by commit failure can produce an unusable emailed link. A durable outbox/delivery audit remains a production follow-up; no background worker is introduced.

## Privacy and release blockers
Activation responses use no-store and no-referrer. Password fields use sensitive-POST filtering and are not echoed. Tokens still appear in activation URL paths and browser history: hosting/proxy/APM access logs must redact these paths before operational enablement. Do not paste links into tickets/logs. Console email is development-only. Add activation/password throttling, auth audit, session limits, full browser recovery tests, PostgreSQL race tests, and approved delivery/retention policies before production.

## Verification
Fourteen new tests authored for owner confirmation, delivery rollback, resend, activation, token reuse, role injection, expiry, CSRF, privacy headers, gates, and organization boundaries. Syntax checked only; runtime/CI not run here. Run python manage.py test and migration-drift checks in CI, then local/staging browser acceptance. Previous owner-management commit 0ce5595 passed according to the owner's 08:51 EST report; this increment is not yet verified.
