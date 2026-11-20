# Development Tickets and Fix Ledger

Updated: 2026-11-20. Branch feature/assign-01-student-ui, baseline main 0d445e2 (code 5ee2a7b, tests 248127c).

## ASSIGN-01 — IN_PROGRESS; student UI REVIEW
Authored /students/assignments/ (20 per page) and own-snapshot detail pages, plus a link from student home, GET and HEAD only. They reuse the student backend, database-session guard, feature flag and expiry middleware and the student_assignments query, so the active student, profile, organization, class, enrollment and uncancelled own assignment are required on every request. Another active class does not restore an ended-class assignment. Unknown, foreign and other-student IDs return 404 and query parameters naming a student or organization are ignored. Text is escaped and the LEGO link is shown only if it validates. No roster, documents, writes, progress, feedback, submission or completion controls. No model, migration, settings, password or flag change.

18 HTTP test methods authored (identity and organization isolation, revocation and cancellation, snapshots, escaping, methods and headers, backend and expiry isolation, reset and A/B switching, pagination); existing tests retained. The author checked only Python syntax and compilation; Django tests, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author. The owner reports CI passed on the push of 248127c; not independently retrieved, run and test count unknown. No passing count is inferred.

## Evidence retained
- Owner-reported, not independently retrieved: CI passed for main 0d445e2 (documentation) and for the push of 248127c on this branch. Neither is evidence of a merge-specific post-PR #2 run.
- PR #1 merged at 9012dd1; dddb545 pre-merge checks independently successful (including 44665321805). Run 44665898145 owner-reported.
- PR #2 merged at 92ed0ab; BUG-006 fix ddc000b checks 44668593439 and 44668981076 independently successful. BUG-006 FIXED_VERIFIED for the UUID serialization defect only.
- Initial UI f52a592 run 44667767312 failed (owner-reported; supplied log showed 296 tests, 9 errors, UUID JSON serialization), retained with no derived passing count. BUG-005 after 8e80939 is owner-reported.

## Process note
The student UI landed as three commits (code 5ee2a7b, tests 248127c, then documentation) because the tooling could not carry all files in one push. The code commit message describes the whole feature although it contains only code and templates; code and tests were briefly on the branch without documentation.

## Remaining acceptance
Student browser, back, BFCache, restart, reset and session-race acceptance; durable instructor review-token concurrency; progress, feedback and reporting; student document authorization and file safety. ASSIGN-01 is not completed by this branch.

E08-08 CI_PASSED and BUG-004 FIXED_VERIFIED keep their earlier user-report attribution. E08-05 IN_PROGRESS, BUG-003 REVIEW, and the branding, library and document security, operations and browser acceptance remain open. Audit, throttling, recovery, approved sessions, TLS, privacy, retention, mail, file safety, backups, deployment and training are unresolved. The PDF flag is off with no real-file or student delivery approval.

[Previous ledger](https://github.com/pavanjains/lms/blob/0d445e20a4d70a11df33612e81c3e94e4b82803a/docs/TICKETS.md)
