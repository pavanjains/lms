# Development Tickets and Fix Ledger

Updated: 2026-11-20. Baseline main 220407d (docs after the PR #3 merge at 4695e7d). Branch assign-02-instructor-progress adds ASSIGN-02, not yet merged.

## ASSIGN-02 — IN_REVIEW; instructor progress and feedback, not yet merged
Branch assign-02-instructor-progress adds instructor-controlled progress to each assignment snapshot. Statuses: Assigned (default), In progress, Reviewed, Needs revision; any transition is allowed and only staff can make one. An authorized instructor or owner saves a status and optional feedback (up to 2000 characters) through a confirmed POST to /staff/lessons/assignments/<id>/progress/. The service update_progress mirrors cancel_assignment: it locks the actor, assignment and active class, requires a current integer expected_version, rejects cancelled assignments and archived classes, and advances the version. A migration (0003) adds progress, feedback, progress_updated_at and progress_updated_by with two database check constraints (valid status; update time and updater set together).

Decision recorded 2026-11-20: students see the status label only. Feedback text is staff-only and is not rendered on any student page; the student templates never reference it. Students get no progress, completion or submission controls.

22 test methods are in apps/lessons/test_assignment_progress.py (service validation, stale-version, authorization, cancelled and archived rejection, database constraints, staff POST, CSRF, escaping, and student status-only and no-feedback checks). The author checked only Python syntax with ast parsing; Django tests, migrations, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author, and no CI result exists for this branch yet. Student pages now show the stored status; with the default, their text is still "Status: Assigned", so the existing student test is unchanged.

Risks to check in CI: the migration must match the model state exactly (makemigrations --check), and student and staff routes must keep their existing 302, 403 and 404 behavior.

## ASSIGN-01 — IN_PROGRESS; student UI MERGED, acceptance pending
PR #3 merged the student read-only assignment pages into main at merge commit 4695e7d510aa6811b27738725feeb95c4c787104 (PR head ebdb9ea). Student pages reuse the student backend, session guard, feature flag, expiry middleware and the student_assignments query. 18 HTTP test methods exist for them. Two check runs on PR head ebdb9ea were independently retrieved as successful: 44834522871 and 44834596308 (no test count exposed). The owner reports CI succeeded for main commits 4695e7d, a034438 and 5762135, and on 2026-11-20 stated that CI is a success; no run IDs or counts were provided and none were independently retrieved.

## Evidence retained
- Independently retrieved: PR #3 head ebdb9ea checks 44834522871 and 44834596308, success. PR #3 merged at 4695e7d.
- Owner-reported, not independently retrieved: CI succeeded for main commits 4695e7d, a034438 and 5762135; CI passed for main 0d445e2 and for the push of 248127c.
- PR #1 merged at 9012dd1; dddb545 pre-merge checks independently successful (including 44665321805). Run 44665898145 owner-reported.
- PR #2 merged at 92ed0ab; BUG-006 fix ddc000b checks 44668593439 and 44668981076 independently successful. BUG-006 FIXED_VERIFIED for the UUID serialization defect only.
- Initial UI f52a592 run 44667767312 failed (owner-reported; supplied log showed 296 tests, 9 errors, UUID JSON serialization), retained with no derived passing count. BUG-005 after 8e80939 is owner-reported.

## Remaining acceptance
Student and staff browser, back, BFCache, restart, reset and session-race acceptance; independent retrieval of post-merge CI run IDs and test counts; durable instructor review-token concurrency; reporting; student document authorization and file safety; ASSIGN-02 CI, review and merge. ASSIGN-01 is not completed by these changes.

E08-08 CI_PASSED and BUG-004 FIXED_VERIFIED keep their earlier user-report attribution. E08-05 IN_PROGRESS, BUG-003 REVIEW, and the branding, library and document security, operations and browser acceptance remain open. Audit, throttling, recovery, approved sessions, TLS, privacy, retention, mail, file safety, backups, deployment and training are unresolved. The PDF flag is off with no real-file or student delivery approval. A progress migration must be applied by a deliberate deployment step; none was performed.

[Previous ledger](https://github.com/pavanjains/lms/blob/220407dd3f502b0ac736db6417a0af28e3b767df/docs/TICKETS.md)
