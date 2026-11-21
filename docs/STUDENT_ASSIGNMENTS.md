# ASSIGN-01 student read-only workspace

Merged to main by PR #3 (merge commit 4695e7d; PR head ebdb9ea; code 5ee2a7b, tests 248127c). Status: merged, browser and concurrency acceptance pending, not runtime-verified. ASSIGN-01 as a whole remains IN_PROGRESS. The status label described under "Progress status" is in open PR #4 and is not merged.

## Routes and behavior
- /students/assignments/ (student-assignment-list): paginated list (20 per page) of the signed-in student's own active assignment snapshots.
- /students/assignments/<assignment_id>/ (student-assignment-detail): the student's own eligible snapshot. Unknown and inaccessible IDs both return 404.
- Student home links to "My assigned lessons". Identity, grade and class display and the CSRF-protected POST sign-out are unchanged.

The list shows title, the student's own class name, kit and a status label. The detail page shows the snapshot title, summary, instructions, kit, grade range and source lesson version, plus a link to the LEGO page only when the stored URL passes the existing validator. All text is autoescaped and instructions render as text.

There is no roster, no other student's identity, no document download, no feedback display, no progress editor, and no submission or completion control. The sign-out form is the only form on these pages.

## Progress status (PR #4, not merged)
Decision 2026-11-20: students see the instructor-set status only. The status is one of Assigned, In progress, Reviewed or Needs revision and defaults to Assigned, so the text "Status: Assigned" is unchanged until an instructor updates it. Instructor feedback text is staff-only and is not rendered or queried by any student template. Students cannot change status.

## Authorization and session boundaries
Every request re-runs student_assignments, so the student, profile, organization, class, enrollment and uncancelled-assignment checks are fresh. Query parameters naming a student or organization are ignored. An active enrollment in a different class does not restore an assignment from an ended enrollment. Editing or archiving the source lesson leaves the snapshot readable while the assignment stays eligible. Cancelling removes it from student pages while staff history is retained.

The views require the student feature flag, a supported database session engine, and a session authenticated through the student backend. Staff sessions are denied. Existing /students/ middleware supplies idle and absolute expiry and the private, no-store, no-cache and same-origin referrer headers on every response, including denials. Only GET and HEAD are accepted.

Headers do not erase an already-rendered page, history entry, screenshot or every BFCache case, and in-flight requests are not cancelled retroactively. Real browser acceptance remains required.

## Verification status
18 HTTP test methods are in apps/lessons/test_student_views.py. PR #4 adds two student-facing checks in test_assignment_progress.py (status shown, feedback never shown). Two check runs on the PR #3 head ebdb9ea were independently retrieved as completed successfully (44834522871 and 44834596308); the API exposes no test count. The owner reports CI succeeded for 4695e7d, a034438 and 5762135; not independently retrieved. Two check runs on the PR #4 head 23a9d2d (44846492681 and 44846822307) were independently retrieved as completed successfully, with no test count. The author ran no browser checks.

## Safety and follow-up
The merged student pages have no model, migration, settings, password, middleware or feature-flag change. PR #4 adds a model migration (0003) that is not applied anywhere. Uploads remain disabled. Next: review and merge of PR #4, then the browser checks in LOCAL_TESTING.md. Instructor review-token consumption under concurrency, reporting and assignment-aware document delivery remain separate work.
