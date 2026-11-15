# E05 owner management UI — increment 1

Tickets: E05-05 (revoke controls), E05-06 (instructor/invitation list).
Status: implemented, CI PENDING; runtime and browser checks not executed here.

## Delivered
- /staff/owner/instructors/: owner-only organization-scoped lists, search, 25-row pagination, active/inactive and pending/expired/revoked/accepted labels.
- /staff/owner/invitations/<id>/revoke/: GET confirmation, explicit confirmed POST, CSRF, lifecycle conflict handling.
- Owner-only staff navigation link; same MFA and feature gate as existing staff pages.
- Fifteen tests covering authorization, isolation, secret non-disclosure, pagination, CSRF, and revocation.

No invitation is issued or emailed by this increment. No public acceptance route, resend button, deactivation control, class assignment, or production activation is introduced. No schema migration is required.

## Manual acceptance after CI
Enable LMS_STAFF_AUTH_ENABLED only in local/staging. Complete owner MFA, open the management link, search accounts, review statuses, and revoke a synthetic pending invitation. Verify an instructor gets denied and tokens/digests never appear. Existing invitations must come from test fixtures or authorized service use until creation/delivery UI is implemented.

## Remaining E05 work
Invite form, email delivery with failure policy, activation form, resend, account deactivation, audit events, PostgreSQL concurrency tests, browser UAT. Keep E05 open.
