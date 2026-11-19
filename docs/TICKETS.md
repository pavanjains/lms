# Development Tickets and Fix Ledger

Updated: 2026-11-18, 21:21 EST.

## Evidence/history
[Previous full ledger](https://github.com/pavanjains/lms/blob/ded6acb393cb80f20bd3394e6f7c3724ccb40ec7/docs/TICKETS.md) preserves E01–E22, E08 details, BUG and commit evidence. REVIEW = authored awaiting verification; CI_PASSED does not close browser/production gates. Markdown IDs are not GitHub Issues. LESSON-01 is a new slice ID under the content roadmap, not completion of E09–E12.

## New lesson library
LESSON-01 REVIEW: model/initial migration, scoped services, MFA/CSRF staff browser list/detail/create/edit/archive, query/kit/grade/status filters, pagination and tests authored. New CI, migration execution/drift, browser and PostgreSQL concurrent-edit acceptance PENDING. Runtime database untouched here. No upload/assignment/student lesson route, seeds or flag changes. Staff gate off by default. Supporting documents and assignments remain TODO separately.

Same-organization active staff view active library; creator/owner edit/archive. Archived records retained and visible only to creator/owner. Fields: title/summary, HTTPS education.lego.com URL, plain-text instructions, kit, min/max grade, active/version/timestamps and protected organization/creator. Essential grades through 4, Prime 4–8, Grade 4 either kit. Each lesson has one kit; no kit forced on class/student. Server never fetches external URL; no availability/educational suitability assertion. Version token plus lock rejects stale form updates, not a durable audit history.

Tests authored, NOT RUN here: grade/kit/model constraints, URL safety, owner/creator/peer/org/student/gate boundaries, stale edits/archive, filters/escaping, confirmation and CSRF/origin. No passing test count inferred.

## E08 / BUG-004 evidence update
Owner November 18 21:18: CI passed after ded6acb. E08-08 CI_PASSED, BUG-004 FIXED_VERIFIED on user report, not independently retrieved, no URL/count. Historical a372751 failure: owner 21:14 log Ruff F401 at apps/accounts/test_students.py:10:53 unused ClassInstructor, one lint error; no test outcome inferred. ded6acb removes only import, retains all tests/runtime/flags. This library commit not covered by that pass.

E08-01 CI_PASSED 6929d69 from prior owner report/run 43758274124 (fetch failed/count unknown). E08-02/03 7e3792c, E08-04 d437edf, E08-06 873cbb4, E08-07 460d7fa CI_PASSED per owner 21:02 all-CI report; E08-05 7f97933 overall IN_PROGRESS despite reported concurrency CI pass because manual/new races remain. E08-08 ded6acb now reported passing, but browser/BFCache/race/security acceptance remains open.

## Carry-forward / BUG history
Unchanged E01–E22 and E05 statuses remain as preserved ledger: staff recovery/last-owner/throttling/session, invitation delivery/audit/races/privacy and operational gates open. Student library/assignment/document work not implicitly completed. Python 3.14 support unverified.

BUG-001 FIXED_VERIFIED ef6b96c bootstrap ordering, owner November 15 08:11 log 50 tests/four errors/46 passed, pass 08:24. BUG-002 FIXED_VERIFIED 1b4a5dd mail import corrected e3bcfcb: owner 13:21 log 83 entries/one import error/82 passed, no onboarding methods executed/fourteen retained; owner pass 13:28 without count, cd1f580 records report. BUG-003 remains REVIEW for full browser acceptance despite local fix report and included CI pass; 24453d6 no-referrer to same-origin, token-path logging work open. Earlier inferred 031b843 association and old run evidence retained in linked ledger.

No independently retrieved Actions verification or fabricated passing counts. New library SHA assigned on commit; CI PENDING.
