# Implementation Status

Updated: 2026-11-15, 13:29 EST.

[Action plan](../ACTION_PLAN.md) records the roadmap and release gates. [Ticket ledger](TICKETS.md) records tickets, fixes, commits and CI evidence, and supersedes older feature-document verification notes.

## Implemented and committed
- Django foundation, PostgreSQL configuration, initial organization/user/profile migrations.
- Hidden configuration and CI (1311cd3).
- Owner bootstrap (ce49752), corrected by ef6b96c (BUG-001).
- Staff email/password backend and MFA access guard (b3aca8d).
- Gated authenticator enrollment/login, recovery codes, POST logout and staff page (031b843).
- Instructor invitation schema and lifecycle services (d60ab7d).
- Owner instructor/invitation lists, search, pagination, statuses and revoke UI (0ce5595).
- Gated invitation creation, configured-backend email, confirmed resend and instructor activation (1b4a5dd), with fourteen onboarding tests authored.
- Onboarding test mail-import correction (e3bcfcb, BUG-002); passing workflow confirmed by owner at 13:28 EST.

## Latest verification
BUG-002 is FIXED_VERIFIED based on the owner's 13:28 EST confirmation that the workflow passed after e3bcfcb. Onboarding has owner-reported passing-CI evidence. Passing run URL, exact count and logs were not supplied; Actions result was not independently retrieved. No passing count is inferred from the authored tests. Browser acceptance remains pending.

Historical failure retained: owner's 13:21 EST log contained 83 test entries in 0.897s, one import error and 82 passing entries. The failed-module placeholder meant no onboarding test methods executed in that failed run. e3bcfcb corrected from django.contrib import mail to from django.core import mail without removing or disabling tests. The later passing report supersedes the failed run as the latest reported result.

This documentation-only update records that confirmation; its own workflow result remains pending. It does not change code, migrations, credentials, mail configuration or feature flags, and does not send invitations.

## Not operationally complete
Staff authentication and onboarding default off. Passing CI does not establish operational approval or browser acceptance. Throttling, session limits, recovery, activation-path log redaction, approved mail configuration, delivery reliability, concurrency tests and browser acceptance remain open.

Classes, student access, lessons, documents, assignments, progress, feedback, reports, deployment and broader release gates remain incomplete. Historical feature documents and VALIDATION.json do not override current CI evidence. Passing CI alone is not production authorization.
