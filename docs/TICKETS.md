# Development Tickets and Fix Ledger

Updated: 2026-11-19. Current baseline main92ed0ab.

## ASSIGN-01 — IN_PROGRESS
Foundation merged PR #1 at9012dd1, preserving dddb545. Instructor UI merged PR #2 at92ed0ab, preserving f52a592 and ddc000b. Explicit-recipient snapshots, grade/kit checks, transactional creation/versioned cancellation, scoped queries and instructor list/select/review/confirm/detail/history are implemented. No student assignment screens/progress/feedback/reporting/document delivery yet; no submissions/student completion. Browser and assignment/review-session concurrency acceptance open; no durable exactly-once nonce store.

## BUG-006 — FIXED_VERIFIED, pre-merge automated evidence
Original UI f52a592 failed reported run44667767312: supplied paste.txt inspected,296tests/9errors with UUID JSON signing TypeError. Failure retained; no inferred passing count. Correction ddc000b uses str(org UUID) in token and comparison; two UUID regressions added with existing tests retained. Checks job success independently retrieved for run44668593439 and PR-triggered44668981076 at that head. This verifies automated checks, not browser/concurrency/deployment acceptance.

## CI attribution
Foundation checks including44665321805 independently retrieved successful at dddb545. Post-PR1 main44665898145 successful per owner only. BUG-005 after8e80939 remains owner-reported. Post-PR2 main92ed0ab CI NOT VERIFIED. Successful jobs do not supply a verified test count; no current passing totals inferred from authored methods. See VALIDATION.json.

## DOCS local testing/current-state refresh — REVIEW
LOCAL_TESTING.md procedures and ASSIGNMENTS.md added; README,index,decisions,validation and all three tracking docs reconciled. Local commands/browser procedures NOT RUN during documentation preparation; doc-only change, no feature activation/runtime data/schema/credentials. Review procedures on intended local environment before use. Older feature guides retain original increment history; docs/README.md identifies superseding behavior/evidence.

## Remaining acceptance and carry-forward
E08-08 CI_PASSED/BUG-004 FIXED_VERIFIED retain prior user-report attribution. E08-05 IN_PROGRESS, BUG-003 REVIEW, BRAND-01/DOC-01/LESSON-01 outstanding browser/security/operations remain open. Student password/create/login/reset races, shared-device/back-navigation, audit/throttling/recovery/approved sessions/TLS/privacy/retention/mail/file safety/backups/deployment/training unresolved. PDF flag off; no real-file/student delivery approval.

[Complete pre-refresh ledger](https://github.com/pavanjains/lms/blob/92ed0ab127149081483c8044ab41cf4e4ee9f82e/docs/TICKETS.md) preserves earlier BUG/E01-E22/E08 histories, failures/counts/statuses and source links. New passes do not erase older failure evidence or finish broader epics.
