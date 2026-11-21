# Handoff note: Robotics LMS (pavanjains/lms)

Written 2026-11-20 (Friday, 8:06 PM EST). Point-in-time snapshot. TICKETS.md and VALIDATION.json are the source of truth for evidence; this file is for resuming work.

## Where things stand
- main was at f3cc9e2ce34c55047bc27751976939464adeab6f, the merge of PR #4 (ASSIGN-02, instructor progress and feedback), when this note was written.
- Instructors and owners set one of four statuses (Assigned, In progress, Reviewed, Needs revision) and an optional note of up to 2000 characters. Students see the status label only, never the note.
- Migration 0003 is on main but applied nowhere. No database has changed.
- ASSIGN-01 and ASSIGN-02 are both IN_PROGRESS. Nothing is production-approved.
- Merged PRs: #1 at 9012dd1, #2 at 92ed0ab, #3 at 4695e7d, #4 at f3cc9e2.

## Evidence and attribution
| Item | Source | Notes |
|---|---|---|
| PR #4 head f5ec991, runs 44847456934 and 44847462963 | Independently retrieved | Success, no test count |
| PR #4 head 23a9d2d, runs 44846492681 and 44846822307 | Independently retrieved | Success, no test count |
| PR #3 head ebdb9ea, runs 44834522871 and 44834596308 | Independently retrieved | Success, no test count |
| First run on c9b76e2 | Owner-supplied log | 338 tests, 2 failures from one test, run ID not recorded |
| CI on main for f3cc9e2, 4695e7d, a034438, 5762135 | Owner-reported only | Not retrieved, no run IDs |

The API exposes no test counts, so no passing total is recorded anywhere. The author (the AI assistant) has never run Django tests, Ruff, template rendering, browser checks or PostgreSQL race checks; CI is the first real execution of anything written.

## Open items, in priority order
1. Browser acceptance from docs/LOCAL_TESTING.md: the staff progress form, the student status label, student A/B isolation, back/reload, reset, expiry and revocation.
2. Deploy migration 0003 as a deliberate step, after a database backup.
3. Progress history and reporting. Only the latest status and note are kept today.
4. Durable review-token concurrency. There is no exactly-once guarantee for assignment review tokens.
5. Decide whether to enforce TextField max_length in services. full_clean() does not enforce it for Lesson and LessonAssignment summary and instructions. CI found this for feedback only, and it was fixed in the service.
6. Stale docs: README, docs index, DECISIONS, STUDENT_SIGN_IN and LOCAL_TESTING are not updated for ASSIGN-02, and the six tracking docs name baseline 220407d, not the merge commit.
7. Independently retrieve post-merge CI for main if the run is still available.

## Cleanup
Three remote branches were merged and are safe to delete: assign-02-instructor-progress, feature/assign-01-student-ui and feature/assign-01-instructor-ui. Locally: git pull, then git fetch --prune, then git branch --merged main, and delete with git branch -d.

## Working rules settled in this work
- Confirm every write (push, PR, merge) with the exact payload before doing it.
- Record only what was retrieved or reported, with attribution. Never infer a test count or overwrite an earlier failure with a generic pass.
- Develop on a feature branch and open a PR. Direct pushes to main were used only for docs.
- Use the head-SHA guard (expectedHeadSha) on merges.
- Every implementation commit updates ACTION_PLAN.md, TICKETS.md, IMPLEMENTATION_STATUS.md, affected guides and VALIDATION.json.

## Codebase notes
- Assignment code is in apps/lessons (models.py, assignments.py, assignment_views.py, student_views.py, urls.py). Templates are in templates/lessons and templates/students.
- Service pattern: lock the actor, the object and the class, check expected_version, then bump the version. Copy cancel_assignment or update_progress for new writes.
- Test pattern: the progress tests borrow fixtures with setUp = foundation.AssignmentFoundationTests.setUp and use login_staff from the instructor view tests.
- Gotchas: the authoring sandbox resets between messages, so files must be rebuilt in one go. The GitHub push tool takes whole files, not patches. The hand-written migration passed CI's model check.
