# Local testing guide

Updated: 2026-11-20. Written against main 0d445e20a4d70a11df33612e81c3e94e4b82803a plus the authored feature/assign-01-student-ui branch; the student assignment pages are REVIEW, not merged or runtime-verified. These are procedures and expected results, NOT a report that they were executed. Use synthetic people, credentials, lessons and files only. Do not use production/staging databases or real student data.

## 1. Prerequisites and checkout
Python 3.12, Docker Compose and a POSIX-compatible shell. PostgreSQL 16 matches compose.yaml and CI. Windows users may use WSL or translate activation/environment syntax; these shell examples are not PowerShell commands. Do not reuse an unverified Python 3.14 virtual environment. Preserve local changes before switching branches.

```sh
git status --short
# Continue only after preserving any local changes.
git fetch origin
# Test main, or switch to feature/assign-01-student-ui to try the student pages.
git switch main
git pull --ff-only
git rev-parse HEAD
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
test -f .env || cp .env.example .env
```

Edit .env locally. Choose a local-only secret/password and verify POSTGRES_HOST=127.0.0.1, the database name/user/port and allowed loopback hosts. Never commit .env. Source only a trusted shell-compatible file; shell sourcing executes its contents. Django does not automatically load .env.

```sh
set -a
. ./.env
set +a
export DJANGO_SETTINGS_MODULE=config.settings.development
docker compose up -d db
docker compose exec db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Wait/retry the readiness command if PostgreSQL is starting. A port-5432 conflict must be resolved in your local configuration; do not accidentally test against another installation. Existing PostgreSQL volumes retain their initialized users/passwords/databases; editing .env does not rewrite them. Do not delete volumes as a troubleshooting shortcut.

Before any migration, confirm this is your disposable/local environment:

```sh
python manage.py shell -c 'from django.conf import settings; from django.db import connection; d=settings.DATABASES["default"]; print(connection.vendor, d.get("HOST"), d.get("PORT"), d.get("NAME"))'
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
# Writes schema: run only against the reviewed local database.
python manage.py migrate --noinput
```

Expected: PostgreSQL/loopback/local DB, no system-check errors or missing migrations, then successful migration application. Liveness is not a database/storage readiness check. A fresh checkout has no seeded lessons or test accounts.

## 2. Automated verification matching CI
Keep the PostgreSQL environment exported. The local DB account needs permission to create/drop a test database. These commands intentionally use CI settings only for automated checks/tests, not account creation or runserver.

```sh
ruff check .
python manage.py check --settings=config.settings.ci
python manage.py makemigrations --check --dry-run --settings=config.settings.ci
python manage.py test apps.lessons.test_assignment_review_uuid apps.lessons.test_assignment_views apps.lessons.test_assignments --settings=config.settings.ci --verbosity=2
python manage.py test apps.lessons.test_student_views apps.accounts.test_students --settings=config.settings.ci --verbosity=2
python manage.py test apps.classrooms.test_concurrency --settings=config.settings.ci --verbosity=2
python manage.py test --settings=config.settings.ci --verbosity=2
```

The student-page module exists only on the student-UI branch (and on main once merged). The workflow additionally runs migrate --noinput against its disposable PostgreSQL service and asserts connection.vendor == 'postgresql' before the full suite. Locally, review migrate --plan first and apply only to the intended local DB. Exit status 0 is expected; preserve the actual final summary, failures, errors and skips verbatim. Do not infer a full-suite total from authored method counts (for example, the 18 student-page methods). Running the existing classroom concurrency suite is not proof of assignment/review-token or all account/session races.

Optional fast smoke only:

```sh
python manage.py test --settings=config.settings.test
```

SQLite skips PostgreSQL concurrency checks and does not establish locking/migration acceptance on PostgreSQL. Test/CI settings use a fast password hasher: never bootstrap users or run a browser server under them.

## 3. Browser-only local gates and owner
For an isolated synthetic browser trial, explicitly opt in in this shell; repository defaults remain disabled. Restart the server whenever environment settings change.

```sh
export DJANGO_SETTINGS_MODULE=config.settings.development
export LMS_STAFF_AUTH_ENABLED=true
export LMS_STUDENT_AUTH_ENABLED=true
export LMS_INSTRUCTOR_ONBOARDING_ENABLED=true
export LMS_LESSON_DOCUMENTS_ENABLED=false
export LMS_PUBLIC_ORIGIN=http://localhost:8000
python manage.py bootstrap_owner --organization "Synthetic Local Center" --username local-owner --email local-owner@example.test
python manage.py runserver localhost:8000 --settings=config.settings.development
```

Bootstrap prompts privately for a password and applies validators. It is for initial installation, not account recovery; if it refuses an existing nonmatching installation, investigate rather than deleting records. Do not pass passwords on command lines or use createsuperuser.

Use http://localhost:8000 consistently for this trial. Visit /account/login/, use the synthetic owner email, enroll an authenticator, verify MFA, and store synthetic recovery codes privately. No remembered-browser bypass or MFA-disable workaround. Keep the test device clock synchronized. Open /staff/ after MFA and confirm Stembotic branding.

Development mail prints invitation links in the server console. Treat that output and activation URLs as sensitive: do not attach them to CI logs/tickets. No real emails or accounts. Onboarding is gated independently; enabling staff auth alone does not enable invitations.

## 4. Synthetic fixture through supported screens
1. Owner opens instructor management and invites two synthetic instructors. For a negative-access trial, optionally create a third instructor not assigned to the test class. Activate accounts through console-delivered links, then complete their staff MFA setup in separate browser profiles. Instructor invitation/activation does not assign classes automatically.
2. Owner creates a synthetic class and assigns the two instructors. Both should see it; an unassigned instructor should not.
3. From the active class, create Student A and B in Grade 4 and optionally Student C in Grade 5. Use unique local usernames and nonnumeric test-only passwords; no student email. Do not reuse these passwords elsewhere.
4. Create two synthetic lessons via /staff/lessons/: Essential Grade 4 and Prime Grade 4. Use instructor-authored text and a permitted HTTPS education.lego.com URL. Synthetic test paths are not verified real LEGO lessons; an accepted URL is not a content-suitability/availability guarantee.
5. Use owner/instructor/student browser profiles separately. Different tabs in the same profile share one login identity.

## 5. Instructor assignment walkthrough
Start at /staff/lessons/assignments/ or Lesson library > Assignments.

| Check | Expected result |
|---|---|
| Select authorized class, active lesson and explicit A/B recipients | Only authorized active class students and same-org active lessons are offered |
| GET selection, submit Review, leave without confirming | No assignment rows created |
| Review Essential or Prime Grade 4 | Exact students, lesson text, kit, grade range and source version shown; either kit works for Grade 4 |
| Select Grade 5 C for Grade 4 lesson | Incompatible selection rejected; no partial batch |
| Confirm without required checkbox or with altered token | Rejected; no assignment creation |
| Edit/archive source lesson in another authorized session before confirmation | Stale review rejected; select/review again |
| Remove membership/enrollment or deactivate account before confirmation | Rejected on fresh authorization |
| Valid confirmed review | One assignment per reviewed student, followed by history/list; new unreviewed posted IDs cannot replace recipients |
| Submit duplicate active class/student/lesson | Rejected without creating assignments for other selected students |
| Edit/archive lesson after assigning | Existing assignment detail retains original snapshot/version |
| Enroll another student afterward | No automatic assignment to the newcomer |
| Open detail as unassigned instructor/other organization | Denied/not found, no peer-class leakage |
| GET cancellation or omit checkbox/use stale version | No cancellation; successful cancellation requires authorized POST and current version |
| Cancel validly | History retained, cancellation shown; later explicit reassignment permitted |
| Start another review or wait beyond 15 minutes | Older/expired review rejected |

Review-token expiry is separate from login expiry. Normal successful confirmation consumes its session token; durable exactly-once consumption across concurrent requests is not implemented. Concurrent confirm/cancel/session interleavings remain acceptance work. Use the automated tests for signed-token/CSRF/origin cases; never disable CSRF or add null to allowed origins to make a test pass.

## 6. Shared students and student sign-in
Use /students/login/ with an instructor-created synthetic account in a student-only profile. Expected student home: own display name/grade, active class names and a My assigned lessons link. On the student-UI branch, /students/assignments/ (list) and /students/assignments/<id>/ (detail) show only the signed-in student's own uncancelled, currently eligible snapshots; on main before that branch merges these pages do not exist. "Assigned" is an availability label, not progress. No roster, documents, student submissions or completion controls.

Check A sign-out followed by B sign-in, browser Back/reload and no disclosure of A's identity, classes or assigned lessons. As Student B, open A's assignment detail URL and add student_id or organization_id query parameters: expect 404 with no other student's data. As staff in another profile, cancel an assignment, end an enrollment, or archive the class: the item should disappear from A's list and detail on the next request. Editing or archiving the source lesson should leave A's snapshot unchanged. Instructions containing markup should display as text, and responses should be private/no-store with a same-origin referrer policy.

Verify student attempts to open /staff/lessons/assignments/ are denied, staff cannot silently replace a student login, and owner/instructor sessions in other profiles are unaffected. Review target-only password reset/session revocation with synthetic credentials; never record receipt passwords. Default student idle is 900 seconds and absolute is 14400 seconds, enforced on subsequent requests; this is not per-tab isolation or instant removal of already-rendered pages. Full back/BFCache/restart/reset/sign-in race acceptance remains open.

## 7. Optional protected-PDF trial
Keep uploads disabled for normal testing. Only for an isolated approved synthetic-fixture trial, export LMS_LESSON_DOCUMENTS_ENABLED=true and restart development server. Use a trusted inert synthetic PDF; do not fetch/open real student files or treat uploaded files as safe. Test creator/owner upload/archive and permitted staff download, denial of peer mutation/other-org/student access, stale versions, size/quota handling and retention after archive. Restore the flag to false and restart afterward.

Current limits: 5 MiB/file,20 active/lesson,100 MiB/org including archived bytes; private database BLOBs, no public URLs. Signature/end-marker/integrity checks are not full PDF validation or malware scanning. No assignment-aware student document delivery exists. Do not open downloaded test files merely to prove download authorization. See LESSON_DOCUMENTS.md for detail.

## 8. Troubleshooting without bypassing controls
- Staff/student/onboarding 404: verify the relevant gate and development settings, then restart.
- Staff redirect after password: complete MFA; do not remove the guard.
- CSRF 403: use one loopback origin, rendered form token, current cookies and same-origin referrer behavior. Do not exempt views. Historical no-referrer onboarding wording predates its CSRF fix.
- No classes/students: verify active organization/class, instructor membership and enrollment; existing students are shared through class scope, not creator ownership.
- Review serialization TypeError involving UUID: ensure checkout includes BUG-006 ddc000b or merged main 92ed0ab. Org IDs must be strings inside JSON review tokens and compared consistently. Preserve all token/authority checks.
- Stale review: select and review again; do not edit hidden expected-version fields.
- Test DB permission/connection/port errors: inspect local host/DB/role and Compose health; never point tests at production or delete persistent volumes as a shortcut.

## 9. Evidence and cleanup
Record: UTC/local timestamp, git SHA/branch, OS/Python/PostgreSQL/settings, test command, exit status, verbatim summary/skips and each browser case as PASS/FAIL/NOT RUN/BLOCKED. Mark evidence as independently retrieved, owner-reported, supplied log inspected, local command executed or procedure-only. Redact passwords, cookies, OTP secrets, recovery codes and invitation/review tokens.

No browser acceptance is claimed by this document. Do not change pending to passed without observed evidence. Sign out all profiles, disable local gates when finished and stop the server. docker compose stop db stops the local container without intentionally deleting its volume. Do not use down -v or production reset/delete commands as routine cleanup.

## 10. Documentation maintenance
Every implementation/fix commit must update ACTION_PLAN.md, TICKETS.md and IMPLEMENTATION_STATUS.md and any affected current feature/testing/setup/decision docs. Update VALIDATION.json only with attributed evidence. Keep earlier failure history. Update the documentation index when adding or superseding a guide. This policy is applied with changes; it is not an unattended synchronization service.
