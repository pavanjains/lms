# BRAND-01 Stembotic / DOC-01 lesson documents

Status REVIEW: authored, not executed here; CI/migration/browser/concurrency/real-file/restore acceptance pending. No production file handling approved.

## Branding
Shared base header and browser title include Stembotic, including MFA inheritance. Production error templates and generic CSRF failure page use same base; no sensitive failure reason reflected. Machine JSON liveness, user-uploaded PDF bytes, Django DEBUG tracebacks and framework-generated method responses are not rewritten.

## PDF support documents
Local synthetic trial: export LMS_LESSON_DOCUMENTS_ENABLED=true in local .env and restart. Default false remains in repository. Staff with MFA open lesson detail, Supporting documents. Creator/owner can upload a PDF title/file/confirmation with current parent version; others can download if lesson visible. No student access until assignment-specific authorization exists.

Limits: 5 MiB per PDF,20 active/lesson,100 MiB organization total including archives. Database BLOB storage deliberately used for this small-center slice: no public media paths, filesystem writes or object-store URL exposure; metadata/content/parent-version/quota checks transactional. This increases DB/backup size. Review and test encrypted backups/restore before real usage; storage scaling/object store and retention/deletion remain future work.

Validation checks filename extension/length/control characters, declared plus actual bounded bytes, PDF header/end marker, and metadata/SHA-256 consistency. It does not fully parse PDF or detect malware, scripts, embedded content, polyglots or malicious readers. MIME header is not trusted as evidence. Forced attachment/application-octet-stream/nosniff/CSP reduce browser execution risk but do not make opening a file safe. No previews, parsing/execution, extraction or external fetch. Scanner/CDR/parser policy is a production blocker.

Download authorizes before serving bytes and verifies length/checksum; safe application-generated download filename. Metadata lists do not fetch BLOBs. Archive is logical: downloads hidden, bytes remain/quota counted, no hard-delete/reactivation. Archived parent lesson read policy still limits retained document downloads to creator/owner. Expected lesson version guards upload/archive against concurrent metadata/document changes; stale forms rejected, not auto-retried. Duplicate uploads allowed within quota. Direct ORM bypass remains privileged.

Django may spool multipart bodies before view validation; web server/proxy request-size and rate limits are required before production. No antivirus, durable audit, upload throttling or student delivery in this increment. Use only trusted synthetic fixtures locally; no real children/files enabled by source commit.

## Verify
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
python manage.py migrate
python manage.py test apps.documents apps.core.test_branding --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

Browser: verify Stembotic on home/staff/student/MFA/error pages, then synthetic PDF upload/list/download/archive, blocked peer mutation/foreign access/student access, unconfirmed POST/CSRF, size/quota/stale version, archive retains bytes but blocks downloads. Real-file opening and PostgreSQL parallel upload/quota races require further acceptance. Record actual outputs/revision separately; never infer pass/counts from authored tests.
