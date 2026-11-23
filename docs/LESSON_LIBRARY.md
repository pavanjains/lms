# LESSON-01 staff lesson library and text validation

Updated 2026-11-22 for fix/lesson-text-validation, baseline main ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6. Validation hardening is authored, CI pending; no production approval. Earlier library increment notes are historical, not a new verification report.

## Existing workflow retained
MFA-verified active staff use /staff/lessons/ to create confirmed lessons with title, summary, instructions, official HTTPS LEGO Education URL, kit and grade range. Active lessons are shared within the organization; creator/owner edit or archive. Archived records are retained, visible to creator/owner; no reactivation/delete workflow. Search/filter/pagination and escaping remain. Essential supports Pre-K/K through Grade4, Prime Grades4-8, Grade4 either kit. Library grades -1/0/1-8 map to student profile strings in assignment services. One kit per lesson; no automatic kit assignment.

URL validation permits only HTTPS education.lego.com, default/443 port and no embedded credentials. No server fetch/scraping/availability or educational-suitability claim. Test URLs are synthetic. Staff must review real content; text is escaped, not raw HTML. Organization/MFA/current actor, editable-field whitelist, ownership, row locks and expected-version checks remain. No durable revision/audit history. Raw ORM/update/bulk bypass is not a supported authorized write path. Later staff documents, explicit snapshot assignments, student own-assignment pages, staff status/feedback and roster entry exist; original missing-feature statements are superseded by current tracking.

## Text-boundary hardening
The service helper validate_lesson_text reads each instance's declared model max_length: summary2000 characters, instructions20000 for both Lesson and LessonAssignment. It raises field-keyed ValidationError entries using MaxLengthValidator; it does not truncate or mutate content. Blank summary remains allowed; blank instructions remain rejected by existing model cleaning.

create_lesson and update_lesson run the helper after full_clean and before save. create_assignments revalidates the source and each snapshot after normal cleaning and before insertion. Existing instruction strip behavior is retained, summary whitespace is retained, and length counts Python string characters rather than encoded bytes. Invalid edits must leave stored content/version/timestamp unchanged; any snapshot failure must roll back the entire assignment batch. HTTP forms/messages, title/URL rules, feedback validation, cancellation/progress/archive behavior and authorization are not changed.

No model fields, migration or DB constraints are added. Existing data is not scanned, repaired or truncated; raw ORM bypass remains possible. Reassignment from an oversized source is rejected until that source is valid. This is service-path enforcement, not a blanket database or model-only guarantee. No observed new production defect or baseline failing run is claimed; the earlier feedback-length failure motivated this source-audited hardening.

## Verification — NOT RUN except new-module syntax
Twelve authored methods in apps/lessons/test_text_validation.py cover create/edit exact and over-limit values, unchanged rejected-edit data/version/timestamp, boundary snapshots, oversized source rejection, second-snapshot rollback, field errors/model limits, whitespace/blank summary, Unicode and authorization guards. New helper/test modules syntax/compile checked only. Django/Ruff/migration-drift/PostgreSQL/browser checks NOT RUN by author; CI pending, no passing count. Existing tests retained.

Use only an isolated test environment; preserve local data/changes and do not rerun bootstrap or apply migrations as part of this no-schema change.

```sh
ruff check .
python manage.py check --settings=config.settings.ci
python manage.py makemigrations --check --dry-run --settings=config.settings.ci
python manage.py test apps.lessons.test_text_validation apps.lessons.tests apps.lessons.test_assignments apps.lessons.test_assignment_views apps.lessons.test_assignment_progress --settings=config.settings.ci --verbosity=2
python manage.py test --settings=config.settings.ci --verbosity=2
```

Browser, concurrency, document safety, logging, privacy, deployment and other existing release gates remain open. Prior guide/history: https://github.com/pavanjains/lms/blob/ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6/docs/LESSON_LIBRARY.md
