# Robotics LMS — Action Plan

Updated: 2026-11-20. Branch feature/assign-01-student-ui, baseline main 0d445e2 (code 5ee2a7b, tests 248127c).

## Current increment — REVIEW
Student read-only assigned-lesson list and detail pages with a link from student home. They reuse the existing student backend, session middleware and student_assignments query, show only the signed-in student's own eligible snapshots (20 per page, "Assigned" availability label, escaped text, validated LEGO link), and accept GET and HEAD only. No roster, peer data, documents, progress editing, submissions or completion controls. No model, migration, settings, middleware, password or flag changes; uploads stay off; no runtime database or credential actions.

18 HTTP test methods are authored, mostly using real student sign-in. The author checked only Python syntax and compilation; Django tests, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author. The owner reports CI passed on the push of 248127c; that was not independently retrieved, and no test count is known. The branch is not merged and ASSIGN-01 remains IN_PROGRESS. See STUDENT_ASSIGNMENTS.md and LOCAL_TESTING.md.

## CI and history evidence
Owner-reported (not independently retrieved): CI passed for main 0d445e2 (documentation) and for the push of 248127c on this branch. PR #1 merged at 9012dd1 and PR #2 at 92ed0ab. Pre-merge checks for dddb545 (including 44665321805) and for ddc000b (44668593439 and 44668981076) were independently retrieved as successful. The original UI revision f52a592 failed run 44667767312 (owner-reported; supplied log showed 296 tests, 9 errors from UUID JSON serialization), retained as history. BUG-005 and run 44665898145 remain owner-reported. A merge-specific post-PR #2 run is unverified.

## Next
1. Independently retrieve the CI run for this branch and record jobs and counts only if retrieved.
2. Run the browser A/B, back/reload, reset, expiry, revocation, escaping and header checks from LOCAL_TESTING.md.
3. Review assignment, review-session, reset and sign-in concurrency and a durable review-token design; no exactly-once guarantee exists today.
4. Add instructor-controlled progress, status and feedback, then reporting. Assignment-aware document delivery needs separate authorization and file-safety work. Submissions and student-controlled completion stay excluded.

## Release gates retained
Branding, document and lesson-library browser, security and operations acceptance; E08-05 and BUG-003; shared-device, back-navigation, reset and sign-in races; audit, throttling, recovery, approved session policy, TLS, log redaction, privacy, retention, email, deployment, backup and restore, and training. PDFs stay disabled outside controlled synthetic trials with no malware scanning or full parser. Python 3.14 is unverified. No production authorization.

Every implementation or fix commit updates this plan, TICKETS.md, IMPLEMENTATION_STATUS.md and affected current guides, decisions and validation. [Previous plan](https://github.com/pavanjains/lms/blob/0d445e20a4d70a11df33612e81c3e94e4b82803a/ACTION_PLAN.md)
