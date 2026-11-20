# Development Tickets and Fix Ledger

Updated: 2026-11-20. Baseline main 4695e7d (PR #3 merge).

## ASSIGN-01 — IN_PROGRESS; student UI MERGED, acceptance pending
PR #3 merged the student read-only assignment pages into main at merge commit 4695e7d510aa6811b27738725feeb95c4c787104 (PR head ebdb9ea; commits 5ee2a7b code, 248127c tests, 2070da8 and bab84d3 and ebdb9ea documentation). /students/assignments/ (20 per page) and own-snapshot detail pages, plus a link from student home, GET and HEAD only. They reuse the student backend, database-session guard, feature flag and expiry middleware and the student_assignments query, so the active student, profile, organization, class, enrollment and uncancelled own assignment are required on every request. Another active class does not restore an ended-class assignment. Unknown, foreign and other-student IDs return 404 and query parameters naming a student or organization are ignored. Text is escaped and the LEGO link is shown only if it validates. No roster, documents, writes, progress, feedback, submission or completion controls. No model, migration, settings, password or flag change.

18 HTTP test methods exist (identity and organization isolation, revocation and cancellation, snapshots, escaping, methods and headers, backend and expiry isolation, reset and A/B switching, pagination); existing tests retained. The author checked only Python syntax and compilation; Django tests, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author. Two check runs on PR head ebdb9ea were independently retrieved as completed successfully: 44834522871 and 44834596308. The API exposes no test count, so no passing total is recorded. The owner reports CI succeeded for the merge commit 4695e7d and the later docs commits a034438 and 5762135; this was not independently retrieved and no run IDs or test counts were provided.

## Evidence retained
- Independently retrieved: PR #3 head ebdb9ea checks 44834522871 and 44834596308, success. PR #3 merged at 4695e7d.
- Owner-reported, not independently retrieved: CI succeeded for main commits 4695e7d, a034438 and 5762135; CI passed for main 0d445e2 (documentation) and for the push of 248127c on the student branch.
- PR #1 merged at 9012dd1; dddb545 pre-merge checks independently successful (including 44665321805). Run 44665898145 owner-reported.
- PR #2 merged at 92ed0ab; BUG-006 fix ddc000b checks 44668593439 and 44668981076 independently successful. BUG-006 FIXED_VERIFIED for the UUID serialization defect only.
- Initial UI f52a592 run 44667767312 failed (owner-reported; supplied log showed 296 tests, 9 errors, UUID JSON serialization), retained with no derived passing count. BUG-005 after 8e80939 is owner-reported.

## Process note
The student UI landed as separate commits (code 5ee2a7b, tests 248127c, then documentation) because the tooling could not carry all files in one push. The code commit message describes the whole feature although it contains only code and templates; code and tests were briefly on the branch without documentation. The branch was merged only after its documentation was complete and its checks were green.

## Remaining acceptance
Student browser, back, BFCache, restart, reset and session-race acceptance; independent retrieval of post-merge CI run IDs and test counts; durable instructor review-token concurrency; instructor progress, feedback and reporting; student document authorization and file safety. ASSIGN-01 is not completed by this merge.

E08-08 CI_PASSED and BUG-004 FIXED_VERIFIED keep their earlier user-report attribution. E08-05 IN_PROGRESS, BUG-003 REVIEW, and the branding, library and document security, operations and browser acceptance remain open. Audit, throttling, recovery, approved sessions, TLS, privacy, retention, mail, file safety, backups, deployment and training are unresolved. The PDF flag is off with no real-file or student delivery approval.

[Previous ledger](https://github.com/pavanjains/lms/blob/0d445e20a4d70a11df33612e81c3e94e4b82803a/docs/TICKETS.md)
