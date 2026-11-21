# Robotics LMS — Action Plan

Updated: 2026-11-20. Baseline main 220407d (docs after the PR #3 merge at 4695e7d). PR #4 (ASSIGN-02) is open and not merged.

## Current state
Student read-only assigned-lesson list and detail pages are merged to main (PR #3, merge commit 4695e7d, head ebdb9ea) with a link from student home. They reuse the existing student backend, session middleware and student_assignments query, show only the signed-in student's own eligible snapshots (20 per page, escaped text, validated LEGO link), and accept GET and HEAD only. No roster, peer data, documents, progress editing, submissions or completion controls.

PR #4 adds instructor-controlled progress and feedback: four statuses (Assigned, In progress, Reviewed, Needs revision), a 2000-character feedback note, a confirmed and version-checked POST for authorized instructors and owners, and migration 0003. Students see the status label only; feedback is staff-only and absent from every student template. The first CI run on c9b76e2 (owner-supplied log) failed one test because the service did not enforce the feedback length; 23a9d2d fixed it. Check runs 44846492681 and 44846822307 on the PR head 23a9d2d were independently retrieved as successful; no test count is available. The author ran no Django tests, Ruff, browser or PostgreSQL race checks. Migration 0003 is not applied anywhere.

18 student-page test methods and 22 progress test methods exist. The owner reports CI succeeded for main commits 4695e7d, a034438 and 5762135; this was not independently retrieved. ASSIGN-01 and ASSIGN-02 remain IN_PROGRESS. See STUDENT_ASSIGNMENTS.md, ASSIGNMENTS.md and LOCAL_TESTING.md.

## CI and history evidence
Independently retrieved: PR #4 head checks 44846492681 and 44846822307 (success); PR #3 head checks 44834522871 and 44834596308 (success); pre-merge checks for dddb545 (including 44665321805) and ddc000b (44668593439 and 44668981076). Owner-reported only: CI for main 4695e7d, a034438 and 5762135, CI for main 0d445e2, the push of 248127c, BUG-005 and run 44665898145. The original UI revision f52a592 failed run 44667767312 (owner-reported; supplied log showed 296 tests, 9 errors from UUID JSON serialization), retained as history. PR #1 merged at 9012dd1, PR #2 at 92ed0ab, PR #3 at 4695e7d. A merge-specific post-PR #2 run is unverified; the post-PR #3 runs are owner-reported only.

## Next
1. Review PR #4 and merge it only after its final head has green checks; then retrieve the post-merge run for main.
2. Independently retrieve the post-merge CI run IDs and test counts for 4695e7d and later main commits; record counts only if retrieved.
3. Run the browser A/B, back/reload, reset, expiry, revocation, escaping and header checks from LOCAL_TESTING.md, including the new staff progress form and the student status label.
4. Review assignment, review-session, reset and sign-in concurrency and a durable review-token design; no exactly-once guarantee exists today.
5. Add progress history and reporting. Assignment-aware document delivery needs separate authorization and file-safety work. Submissions and student-controlled completion stay excluded.
6. Decide whether to enforce TextField max_length in services for Lesson and LessonAssignment summary and instructions; full_clean() does not enforce it.

## Release gates retained
Branding, document and lesson-library browser, security and operations acceptance; E08-05 and BUG-003; shared-device, back-navigation, reset and sign-in races; audit, throttling, recovery, approved session policy, TLS, log redaction, privacy, retention, email, deployment, backup and restore, and training. A deliberate deployment step is needed to apply migration 0003. PDFs stay disabled outside controlled synthetic trials with no malware scanning or full parser. Python 3.14 is unverified. No production authorization.

Every implementation or fix commit updates this plan, TICKETS.md, IMPLEMENTATION_STATUS.md and affected current guides, decisions and validation. [Previous plan](https://github.com/pavanjains/lms/blob/220407dd3f502b0ac736db6417a0af28e3b767df/ACTION_PLAN.md)
