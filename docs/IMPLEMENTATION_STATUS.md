# Implementation Status

Updated: 2026-11-15, 13:21 EST.

[Action plan](../ACTION_PLAN.md) records the roadmap and release gates. [Ticket ledger](TICKETS.md) records tickets, fixes, commits, and CI evidence.

## Implemented and committed
- Django foundation, PostgreSQL configuration, initial organization/user/profile migrations.
- Hidden configuration and CI (1311cd3).
- Owner bootstrap (ce49752), corrected by ef6b96c (BUG-001).
- Staff email/password backend and MFA access guard (b3aca8d).
- Gated authenticator enrollment/login, recovery codes, POST logout and staff page (031b843).
- Instructor invitation schema and lifecycle services (d60ab7d).
- Owner instructor/invitation lists, search, pagination, statuses and revoke UI (0ce5595).
- Gated invitation creation, configured-backend email, confirmed resend and instructor activation (1b4a5dd); fourteen onboarding tests authored, but their module failed to import in the supplied CI log.

## Latest failure and correction
Owner supplied a CI log at 13:21 EST: 83 test entries in 0.897s, one import error and remaining 82 entries passed. apps.accounts.test_onboarding imports mail from django.contrib, which prevents all fourteen onboarding methods from loading. BUG-002 changes that import to django.core. No test methods removed or disabled. Fix CI PENDING; runtime tests not run here. Run URL/SHA not supplied; the source matches 1b4a5dd, but Actions results were not independently retrieved.

The 83 entries include unittest's failed-module placeholder; they do not mean the onboarding tests ran or passed. No new passing count is inferred. Latest previously reported passing application commit is 0ce5595, per owner confirmation at 08:51 EST; browser acceptance remains pending.

## Not operationally complete
Staff authentication and onboarding default off. Invitation screens/email/public activation are authored, not verified or operationally approved. No real invitation, migration, credential configuration or feature activation is performed by BUG-002. Throttling, session limits, recovery, activation-path log redaction, approved mail configuration, delivery reliability, concurrency tests and browser acceptance remain open.

Classes, student access, lessons, documents, assignments, progress, feedback, reports, deployment and broader release gates remain incomplete. Historical feature documents and VALIDATION.json do not override current CI evidence. Passing CI alone is not production authorization.
