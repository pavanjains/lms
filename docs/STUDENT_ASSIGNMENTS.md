# ASSIGN-01 student read-only workspace

Branch: feature/assign-01-student-ui, based on main 0d445e2. Code commit 5ee2a7b, tests 248127c. Status REVIEW: authored, not merged, not runtime-verified. ASSIGN-01 as a whole remains IN_PROGRESS.

## Routes and behavior
- /students/assignments/ (student-assignment-list): paginated list (20 per page) of the signed-in student's own active assignment snapshots.
- /students/assignments/<assignment_id>/ (student-assignment-detail): the student's own eligible snapshot. Unknown and inaccessible IDs both return 404.
- Student home links to "My assigned lessons". Identity, grade and class display and the CSRF-protected POST sign-out are unchanged.

The list shows title, the student's own class name, kit and an "Assigned" label. The detail page shows the snapshot title, summary, instructions, kit, grade range and source lesson version, plus a link to the LEGO page only when the stored URL passes the existing validator. All text is autoescaped and instructions render as text. "Assigned" only indicates the lesson is available; it is not an instructor progress tracker.

There is no roster, no other student's identity, no document download, no feedback or progress editor, and no submission or completion control. The sign-out form is the only form on these pages.

## Authorization and session boundaries
Every request re-runs student_assignments, so the student, profile, organization, class, enrollment and uncancelled-assignment checks are fresh. Query parameters naming a student or organization are ignored. An active enrollment in a different class does not restore an assignment from an ended enrollment. Editing or archiving the source lesson leaves the snapshot readable while the assignment stays eligible. Cancelling removes it from student pages while staff history is retained.

The views require the student feature flag, a supported database session engine, and a session authenticated through the student backend. Staff sessions are denied. Existing /students/ middleware supplies idle and absolute expiry and the private, no-store, no-cache and same-origin referrer headers on every response, including denials. Only GET and HEAD are accepted.

Headers do not erase an already-rendered page, history entry, screenshot or every BFCache case, and in-flight requests are not cancelled retroactively. Real browser acceptance remains required.

## Verification status
18 HTTP test methods are in apps/lessons/test_student_views.py. Most use real student sign-in requests; one deliberately uses force_login to prove that a session without timestamps is denied. The existing foundation, instructor-UI and UUID tests are unchanged.

Locally, only Python syntax parsing and compilation were checked (Django is not installed in the authoring environment): Django tests, Ruff, template rendering, PostgreSQL race checks and browser checks were NOT RUN by the author. The owner reports that CI passed on the push of tests commit 248127c; that report was not independently retrieved, so the run, jobs and test count are unverified here. No passing count is claimed from the 18 authored methods.

## Safety and follow-up
No model, migration, settings, password, middleware or feature-flag change. Uploads remain disabled. Next: independently confirm the CI run, then perform the browser checks in LOCAL_TESTING.md. Instructor review-token consumption under concurrency, progress and feedback, reporting and assignment-aware document delivery remain separate work.
