# LESSON-01 staff lesson library

Status REVIEW: code/tests authored, not run here. CI, migration/drift, PostgreSQL edit races and browser acceptance pending. Adds apps/lessons and initial Lesson migration. No seeded lessons or copied LEGO content.

## Workflow
Verified staff open /staff/lessons/ from workspace, create a lesson with title, summary, instructions, official LEGO Education HTTPS link, kit and grade range, confirm and save. Active lessons shared with active staff in same organization, regardless of class membership. Creator/owner only may edit/archive. Archived records retained and visible to creator/owner; no reactivation/delete. No publication/review workflow or documents/assignments/student access yet.

Essential supports Pre-K/Kindergarten through Grade 4 within this center's existing grade vocabulary; Prime supports Grades 4–8. Grade 4 may use either kit. One kit per lesson record; create distinct kit-specific variants where appropriate. No automatic kit selection, assignment or class kit restriction. Library grade integers -1=Pre-K/0=K/1–8 differ from student profile strings; conversion/compatibility enforced in future assignment service.

## Validation/security
Only HTTPS education.lego.com, default/443 port, no embedded credentials. No external server fetch, scraping, embedding, metadata preview or availability/suitability guarantee. Instructor must choose/review actual content. Test link paths are synthetic and not verified lessons. External link opens with noopener/noreferrer, text escaped; raw HTML not supported. Invalid privileged-ORM links not rendered clickable in detail. No student personal data in organization-shared library.

Services recheck active actor/MFA/org and whitelist editable fields; organization/creator/active/version cannot be posted as editable content. Organization then lesson row locks serialize cooperating services. Version token rejects stale edit/archive; no durable revision history/audit introduced. Future assignment behavior must decide snapshot/version retention before exposure. Database enforces kit/grade ranges and nonempty title/version; model full_clean handles text/URL/creator semantics. Raw ORM/update/bulk bypass remains privileged. Duplicate titles allowed for lesson variants.

Search title/summary, filter grade inclusive/kit/status; pagination 20 preserves filters. Invalid filters return 400. Student routes cannot browse this library. Existing staff gate remains off by default; student feature unaffected. No upload endpoint, document access, assignment, completion/submission or feedback control.

## Verify after commit
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
python manage.py migrate
python manage.py test apps.lessons --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

Local synthetic browser acceptance: owner/instructor with MFA creates Essential/Prime Grade 4 lessons; both match grade filter, kit filter separates them. Essential Grade 5/Prime Grade 3 and unsafe links rejected. Peer can read active lesson but not edit/archive; owner can manage either. Creator archives, peer loses visibility, record remains. Different organization/student denied. Stale edit token rejected, GET/cancel/unconfirmed POST never changes records, CSRF works, instructions render escaped. Verify real URL manually; do not claim test path resolves. Record actual revision/environment/results separately.

Next increments: protected supporting-document storage/download, then assignments with grade/kit/history decisions, instructor progress/feedback and read-only student lesson workspace. Existing account/shared-device and production gates remain open.
