# Implementation Status

Updated: 2026-11-20. Baseline main 220407d (docs after the PR #3 merge at 4695e7d). PR #4 is open. Evidence is in TICKETS.md and VALIDATION.json.

## Implemented in source
Stembotic branding; owner bootstrap; gated staff email and MFA, invitations, onboarding, management and deactivation; scoped classroom services and UI; shared student creation and password reset; separately gated student sign-in and session isolation; lesson library and protected staff PDF support; assignment snapshots, services and instructor screens (PRs #1 and #2, merged at 9012dd1 and 92ed0ab); student read-only assignment pages (PR #3, merged at 4695e7d). No production acceptance is implied.

## Instructor progress and feedback (PR #4, open, not merged)
Authorized instructors and owners can set one of four statuses and an optional note of up to 2000 characters on an assignment through a confirmed, CSRF-protected, version-checked POST. The service locks the actor, assignment and active class, rejects stale versions, cancelled assignments and archived classes, and enforces the length limit itself. Only the latest status and note are kept; there is no history and no reporting. Students see the status label only; feedback is not rendered or queried by any student template and students have no write controls. Migration 0003 adds four fields and two database check constraints and is not applied anywhere. 22 test methods exist.

## Student assignment pages (merged, acceptance pending)
Own-snapshot list and detail pages with a student-home link, GET and HEAD only. They reuse the student session backend, flag, expiry middleware and student_assignments filters, so account, profile, organization, class, enrollment and an uncancelled own assignment are required per request. Detail shows snapshot fields, source version and a validated LEGO link. Text is escaped. No roster, peer data, documents, progress editing, submissions or completion controls; the existing logout form remains.

Other-student, foreign, unknown and revoked IDs are not found, and query IDs do not select an identity. An ended enrollment is not bypassed by another class. Editing or archiving the source lesson leaves an eligible snapshot intact and cancelling removes student access. Existing middleware supplies private, no-store and same-origin referrer headers. Rendered pages, history and BFCache are not erased retroactively, so browser acceptance is still required.

Instructor review-token concurrency, progress history, reporting and student document delivery remain separate. ASSIGN-01 and ASSIGN-02 stay IN_PROGRESS and nothing here is production-ready.

## Verification
18 student-page and 22 progress test methods exist. The author checked only Python syntax; Django tests, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author. The first CI run on PR #4's earlier head c9b76e2 (owner-supplied log) failed one feedback-length test, the fix is 23a9d2d, and checks 44846492681 and 44846822307 on head 23a9d2d were independently retrieved as successful with no test count. Checks 44834522871 and 44834596308 on the PR #3 head ebdb9ea were independently retrieved as successful. The owner reports CI succeeded for main commits 4695e7d, a034438 and 5762135 (not independently retrieved; no run IDs or counts) and for main 0d445e2 and the push of 248127c. dddb545 pre-merge checks and the ddc000b runs 44668593439 and 44668981076 were independently retrieved as successful. Run 44667767312 failed for f52a592 (296 tests, 9 errors, owner-supplied log) and is retained. BUG-005 and run 44665898145 are owner-reported.

## Documentation
The student guide, assignment guide, tickets, action plan, status and validation record reflect PR #4 as open. README, documentation index, DECISIONS, STUDENT_SIGN_IN and LOCAL_TESTING have not been updated for ASSIGN-02. Local testing remains procedure-only.

## Release gates
Uploads stay disabled except controlled synthetic testing (private database PDF-only, 5 MiB per file, 20 active per lesson, 100 MiB per organization including archives). Scanning, parsing, request limits, retention, restore and approved storage remain open, as do audit, throttling, recovery, session policy, TLS, log redaction, privacy, mail, deployment, backups, training, E08-05, BUG-003 and branding, library and document acceptance. Applying migration 0003 needs a deliberate deployment step. Python 3.14 is unverified. No production authorization.

[Previous status](https://github.com/pavanjains/lms/blob/220407dd3f502b0ac736db6417a0af28e3b767df/docs/IMPLEMENTATION_STATUS.md)
