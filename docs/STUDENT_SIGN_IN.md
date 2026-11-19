# E08-08 student sign-in and session isolation

Status REVIEW. Authored tests not run here; new CI, race and browser acceptance pending. No migration. Student authentication is separately gated, default off; staff MFA unchanged.

## Local synthetic trial
After committing, with PostgreSQL and local environment configured:
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.accounts.test_students --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

For browser trial only, add LMS_STUDENT_AUTH_ENABLED=true to local .env, export it and restart development server. Keep repository defaults off. Visit http://localhost:8000/students/login/ in a separate browser profile from owner/instructor. Use an instructor-created synthetic account/password. No student MFA/email required. /students/ shows own display name/grade and active class names only. Students with no active classes get an empty list. No lesson/feedback implementation or submission/completion buttons.

## Boundaries
One identity per browser profile/cookie jar, not per-tab isolation. Logout required before switching. Staff cannot log in via student credentials and cannot have their session silently replaced; student attempts at staff pages return denial without clearing a valid student session. Separate browser profiles needed for simultaneous staff/student testing. Login accepts no next URL; no public student-ID endpoint. User/profile/org active status and nonstaff flags checked by backend on requests.

Student login flushes anonymous context; Django login rotates CSRF/session state. Uses student_username backend credential so normal staff login cannot fall through to student authentication. Organization then student row locked during password check; outer login transaction persists session before release, coordinating with reset services. A reset deleting a session between login commit and response middleware save can yield SessionInterrupted rather than resurrecting the session; concurrent interleavings still need PostgreSQL acceptance. In-flight requests are not retroactively cancelled.

Provisional defaults: LMS_STUDENT_IDLE_SECONDS=900 and LMS_STUDENT_ABSOLUTE_SECONDS=14400, validated positive idle <= absolute <= 86400. Only /students/ requests renew idle time; absolute time never renewed. Missing/malformed/future/out-of-order timestamps fail closed. Database session expiry shortened to remaining lifetime. No remember-me, but a short-lived cookie may persist across browser restart; always sign out. Expiry enforced server-side on subsequent request, not immediate erasure of an already-rendered screen.

Existing password reset removes target database sessions; Django password auth hash also invalidates sessions on password changes. Other students/staff not reset. Unsupported session engines and disabled flag close student routes. no-store/referrer controls do not erase screenshots, browser history or all BFCache behavior; browser back/reload/cookie replay must be tested.

## Acceptance still required
Student A logout then B login with no A data; failed account-switch leaves existing identity intact; idle/absolute expiry; staff MFA unaffected; student staff/other-student access denied; target reset logs student out without affecting others; account/org/role/profile changes deny; CSRF/method checks; back navigation and browser restart. Session creation/reset/access-removal concurrency tests, throttling/audit/TLS/credential UX and production session-policy approval remain open. These defaults are development choices, not approved real-child access.

Prior documents saying student sign-in is unavailable describe earlier increments; this gated implementation supersedes that limitation only, not their remaining operational gates.
