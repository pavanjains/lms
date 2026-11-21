# Development Tickets and Fix Ledger

Updated: 2026-11-20. Baseline main 220407d (docs after the PR #3 merge at 4695e7d). PR #4 (branch assign-02-instructor-progress) adds ASSIGN-02, open and not merged.

## ASSIGN-02 — IN_REVIEW; instructor progress and feedback, PR #4 open
PR #4 adds instructor-controlled progress to each assignment snapshot. Statuses: Assigned (default), In progress, Reviewed, Needs revision; any transition is allowed and only staff can make one. An authorized instructor or owner saves a status and optional feedback (up to 2000 characters) through a confirmed POST to /staff/lessons/assignments/<id>/progress/. The service update_progress mirrors cancel_assignment: it locks the actor, assignment and active class, requires a current integer expected_version, rejects cancelled assignments and archived classes, and advances the version. Migration 0003 adds progress, feedback, progress_updated_at and progress_updated_by with two database check constraints (valid status; update time and updater set together).

Decision recorded 2026-11-20: students see the status label only. Feedback text is staff-only and is not rendered on any student page; the student templates never reference it. Students get no progress, completion or submission controls. With the default status the student text is still "Status: Assigned".

22 test methods are in apps/lessons/test_assignment_progress.py (service validation, stale-version, authorization, cancelled and archived rejection, database constraints, staff POST, CSRF, escaping, and student status-only and no-feedback checks).

### Defect found by CI (fixed)
The first CI run on c9b76e2 (owner-supplied log; run ID not recorded) ran 338 tests with 2 failures from one test and "System check identified no issues", so the hand-written migration matched the model. The failure was a real defect: TextField(max_length=2000) is not enforced by full_clean(), so update_progress saved a 2001-character note. The form path was already limited; the service was not. Fixed in 23a9d2d by checking the stripped length against FEEDBACK_MAX_LENGTH before any field is assigned. The same TextField pattern on Lesson and LessonAssignment summary and instructions is unenforced by full_clean() and predates this change; it is not addressed here.

### Verification
- Independently retrieved: check runs 44846492681 (push of 23a9d2d) and 44846822307 (opening of PR #4) on head 23a9d2d, both job "checks", completed successfully. The API exposes no test count, so none is claimed for these runs.
- Owner-supplied: the failing first run described above, and the owner's report that CI passed after the fix.
- Not run by the author: Django tests, migrations, Ruff, template rendering, browser and PostgreSQL race checks. Only Python syntax was checked by the author before pushing.
- Not applied anywhere: migration 0003. Applying it is a deliberate deployment step.

## ASSIGN-01 — IN_PROGRESS; student UI MERGED, acceptance pending
PR #3 merged the student read-only assignment pages into main at merge commit 4695e7d510aa6811b27738725feeb95c4c787104 (PR head ebdb9ea). Student pages reuse the student backend, session guard, feature flag, expiry middleware and the student_assignments query. 18 HTTP test methods exist for them. Two check runs on PR head ebdb9ea were independently retrieved as successful: 44834522871 and 44834596308 (no test count exposed). The owner reports CI succeeded for main commits 4695e7d, a034438 and 5762135; no run IDs or counts were provided and none were independently retrieved.

## Evidence retained
- Independently retrieved: PR #3 head ebdb9ea checks 44834522871 and 44834596308, success. PR #3 merged at 4695e7d. PR #4 head 23a9d2d checks 44846492681 and 44846822307, success.
- Owner-reported, not independently retrieved: CI succeeded for main commits 4695e7d, a034438 and 5762135; CI passed for main 0d445e2 and for the push of 248127c.
- PR #1 merged at 9012dd1; dddb545 pre-merge checks independently successful (including 44665321805). Run 44665898145 owner-reported.
- PR #2 merged at 92ed0ab; BUG-006 fix ddc000b checks 44668593439 and 44668981076 independently successful. BUG-006 FIXED_VERIFIED for the UUID serialization defect only.
- Initial UI f52a592 run 44667767312 failed (owner-reported; supplied log showed 296 tests, 9 errors, UUID JSON serialization), retained with no derived passing count. BUG-005 after 8e80939 is owner-reported.

## Remaining acceptance
Student and staff browser, back, BFCache, restart, reset and session-race acceptance; independent retrieval of post-merge CI run IDs and test counts for main; durable instructor review-token concurrency; progress history and reporting; student document authorization and file safety; ASSIGN-02 review and merge. ASSIGN-01 and ASSIGN-02 are not completed by these changes.

E08-08 CI_PASSED and BUG-004 FIXED_VERIFIED keep their earlier user-report attribution. E08-05 IN_PROGRESS, BUG-003 REVIEW, and the branding, library and document security, operations and browser acceptance remain open. Audit, throttling, recovery, approved sessions, TLS, privacy, retention, mail, file safety, backups, deployment and training are unresolved. The PDF flag is off with no real-file or student delivery approval.

[Previous ledger](https://github.com/pavanjains/lms/blob/220407dd3f502b0ac736db6417a0af28e3b767df/docs/TICKETS.md)
