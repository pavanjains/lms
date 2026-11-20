# Robotics LMS — Action Plan

Updated: 2026-11-19. Branch: feature/assign-01-instructor-ui.

## Immediate: BUG-006 UUID review-token correction — REVIEW
Uploaded paste.txt for reported run 44667767312 shows Ran 296 tests, FAILED (errors=9), and repeated TypeError: Object of type UUID is not JSON serializable at assignment_create signing.dumps. Evidence read from owner-supplied log, not independently fetched Actions logs. Organization.id is UUIDField. UI f52a592 passed the raw organization UUID to JSON signing.

Focused correction stringifies organization ID in the signed payload and compares it against str(user.organization_id) on confirmation. Other IDs, signature/session/actor/class/expiry/permission checks unchanged. Adds two explicit UUID regressions: successful review-to-confirm round trip and denial of a validly signed different organization. Existing 14 UI methods and 34 foundation methods retained unchanged. No weakening or test removals.

Local standard-library check reproduced original JSON failure and passed normalized JSON round-trip/same-org/different-org comparisons. This is NOT Django test verification. New Django tests/full CI/Ruff/template/browser/concurrency rerun PENDING; no fix-pass or passing test count claimed. No schema/migration/settings/password/flag changes or runtime credential/data actions.

## ASSIGN-01 scope
Instructor UI REVIEW; overall IN_PROGRESS. Scoped list/class selection, explicit lesson/recipients, signed session-bound 15-minute review, confirmation/detail/history and POST-only versioned cancellation authored. Normal success consumes session review; no durable exactly-once concurrency guarantee. Student pages/progress/feedback/documents/completion controls remain outside this increment. Uploads disabled.

## Foundation evidence
PR #1 merged at 9012dd1. Two checks jobs independently confirmed successful for dddb545, including run 44665321805. Post-merge run 44665898145 passed per owner only; no count inferred. BUG-005 CI after 8e80939 remains user-reported. These do not establish a new UI pass.

## Next
1. Commit BUG-006 after review; run UUID/UI/foundation tests, full PostgreSQL CI and Ruff.
2. Browser and concurrent review/confirmation acceptance; then student read-only workspace, instructor progress/feedback/reporting.

All security/operations gates retained: file safety, audit/throttling/recovery/session/races/privacy/retention/mail/backups/deployment/training; Python3.14 unverified. No production authorization.

[Complete pre-fix plan/history](https://github.com/pavanjains/lms/blob/f52a5928f697f6f13b283e1fa74a157710bd2e64/ACTION_PLAN.md). Update all three tracking docs per implementation/fix.
