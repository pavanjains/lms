# Implementation Status

Updated: 2026-11-15, 15:19 EST.

ACTION_PLAN.md records roadmap; docs/TICKETS.md is authoritative for ticket/evidence status. [Preserved previous status](https://github.com/pavanjains/lms/blob/24453d623785f1ff560c3444bcb5eedbb564a36c/docs/IMPLEMENTATION_STATUS.md).

## Current E08-01 increment
apps/classrooms contains Classroom, ClassInstructor and ClassEnrollment models; AppConfig registered in base settings; initial migration and model tests authored. Classes belong to organizations; accounts may have multiple class links. Database uniqueness protects normalized class names within an organization and each class/account relationship. Model clean validates creator role/organization, membership/enrollment roles and organization, active link eligibility and student-profile presence.

Relationships use PROTECT and is_active to support retaining records. No automatic cascade activation/deactivation is implemented. Deactivated instructors retain memberships; future policies must deny access based on current account, organization, class and link status. No fixed kit/grade/capacity imposed on classes.

Tests authored, NOT RUN here. CI, migration drift check and migration execution PENDING. No database modified here, no data seeded. No routes/UI, scoped permission services, student sign-in or account creation. clean/full_clean is validation, not authorization; save/create/update/bulk writes can bypass it. Cross-record consistency is not guaranteed by ordinary foreign keys. E08-02 services and E08-03 policies are next; do not expose these tables through generic CRUD.

## Existing implemented slices
- Organization/user/student-profile foundation and PostgreSQL/CI configuration (1311cd3).
- Owner bootstrap ce49752 corrected by ef6b96c, BUG-001.
- Staff email/password backend and MFA guard b3aca8d; gated MFA enrollment/login, recovery codes, POST logout/workspace 031b843.
- Invitation services d60ab7d; owner lists/search/pagination/revoke 0ce5595.
- Invite/email/resend/activation 1b4a5dd; mail-import fix e3bcfcb, BUG-002; verification recorded cd1f580.
- E05-07 deactivation 666eee6: owner confirmation, retained account/password/MFA, targeted unexpired database-session revocation; unsupported engines rejected. Fourteen tests authored; CI/browser acceptance pending. In-flight requests not retroactively cancelled.
- BUG-003 24453d6: same-origin onboarding header, updated assertion and five new CSRF regression methods; original fourteen onboarding methods retained. Owner confirmed one-line local invitation fix 15:07 EST; new CI/full browser acceptance pending. Internal token-path log redaction remains open.

## Evidence limits
Latest reported passing application revision remains e3bcfcb (owner 13:28 EST). URL/count/logs unavailable; Actions not independently retrieved. BUG-002 remains FIXED_VERIFIED. Historical 13:21 log: 83 entries in 0.897s, one onboarding module-import error, other 82 passed; no onboarding methods executed. No new passing counts inferred. cd1f580 has no separately supplied workflow result.

## Remaining / release boundaries
E08-02/03 services/policies TODO; E08-04 UI and E08-05 race/browser verification TODO. Student access, content/documents/assignments, progress/feedback/reports and deployment remain incomplete. Staff authentication/onboarding flags remain disabled by default; local owner-enabled flags are not production approval. Python 3.14 support remains unverified and local metadata edits are not included.

Recovery, throttling, session limits, last-owner protections, reactivation, audit, PostgreSQL races, approved mail transport/origin/sender/delivery, token-path log redaction, shared-device isolation, privacy/retention, backups/restore and operational acceptance remain open. Passing CI alone is not launch authorization.
