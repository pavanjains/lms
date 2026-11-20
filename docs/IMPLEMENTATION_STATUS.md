# Implementation Status

Updated: 2026-11-20. Baseline main 4695e7d (PR #3 merge). Evidence is in TICKETS.md and VALIDATION.json.

## Implemented in source
Stembotic branding; owner bootstrap; gated staff email and MFA, invitations, onboarding, management and deactivation; scoped classroom services and UI; shared student creation and password reset; separately gated student sign-in and session isolation; lesson library and protected staff PDF support; assignment snapshots, services and instructor screens (PRs #1 and #2, merged at 9012dd1 and 92ed0ab); student read-only assignment pages (PR #3, merged at 4695e7d). No production acceptance is implied.

## Student assignment pages (merged, acceptance pending)
Own-snapshot list and detail pages with a student-home link, GET and HEAD only. They reuse the student session backend, flag, expiry middleware and student_assignments filters, so account, profile, organization, class, enrollment and an uncancelled own assignment are required per request. Detail shows snapshot fields, source version and a validated LEGO link; "Assigned" is an availability label only. Text is escaped. No roster, peer data, documents, progress editing, submissions or completion controls; the existing logout form remains.

Other-student, foreign, unknown and revoked IDs are not found, and query IDs do not select an identity. An ended enrollment is not bypassed by another class. Editing or archiving the source lesson leaves an eligible snapshot intact and cancelling removes student access. Existing middleware supplies private, no-store and same-origin referrer headers. Rendered pages, history and BFCache are not erased retroactively, so browser acceptance is still required.

No model, migration, settings, middleware, password or flag change; no runtime credential, data or schema action; uploads stay disabled. Instructor review-token concurrency, progress, feedback, reporting and student document delivery remain separate. ASSIGN-01 stays IN_PROGRESS and nothing here is production-ready.

## Verification
18 HTTP test methods exist. The author checked only Python syntax and compilation; Django tests, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author. Checks 44834522871 and 44834596308 on the PR #3 head ebdb9ea were independently retrieved as successful; no test count is available. CI for the merge commit 4695e7d has not been checked. The owner reports CI passed for main 0d445e2 and for the push of 248127c (not independently retrieved). dddb545 pre-merge checks and the ddc000b runs 44668593439 and 44668981076 were independently retrieved as successful. Run 44667767312 failed for f52a592 (296 tests, 9 errors, owner-supplied log) and is retained. BUG-005 and run 44665898145 are owner-reported.

## Documentation
The student guide, assignment guide, three tracking docs and validation record reflect the PR #3 merge. README, the documentation index, DECISIONS, STUDENT_SIGN_IN and LOCAL_TESTING still describe the student pages as on a branch awaiting merge and are queued for a follow-up docs commit. Local testing remains procedure-only.

## Release gates
Uploads stay disabled except controlled synthetic testing (private database PDF-only, 5 MiB per file, 20 active per lesson, 100 MiB per organization including archives). Scanning, parsing, request limits, retention, restore and approved storage remain open, as do audit, throttling, recovery, session policy, TLS, log redaction, privacy, mail, deployment, backups, training, E08-05, BUG-003 and branding, library and document acceptance. Python 3.14 is unverified. No production authorization.

[Previous status](https://github.com/pavanjains/lms/blob/0d445e20a4d70a11df33612e81c3e94e4b82803a/docs/IMPLEMENTATION_STATUS.md)
