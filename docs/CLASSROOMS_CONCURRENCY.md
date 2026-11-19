# E08-05 PostgreSQL concurrency verification

Status: concurrency tests authored/REVIEW, not run here; CI pending. Overall E08-05 IN_PROGRESS, browser acceptance open.

## Harness
TransactionTestCase commits fixtures so worker sessions can see them. Each worker opens its own default database connection, records pg_backend_pid, sets READ COMMITTED, 15-second lock_timeout and 20-second statement_timeout, loads its actor and stubs MFA proof for service-unit purposes. Real services execute unchanged.

Leader service runs inside an outer transaction and signals after its write, retaining locks until release. Main starts follower, confirms distinct PIDs, and polls PostgreSQL pg_blocking_pids until leader is reported blocking follower. Only then is leader released to commit. Events/queues/futures have bounds, release happens in finally and workers close connections in finally. Unexpected SQL/deadlock/worker errors fail; only expected PermissionDenied/ValidationError outcomes are classified. Polling is bounded observation, not a sleep-based assumption of overlap.

This intentionally checks ordered concurrent transactions, not which thread wins an uncontrolled race. Leader wait is capped at 40 seconds, observation at 8 seconds, queue/ready waits at 10, future results at 30; CI job at 15 minutes. Timeouts fail and require investigation, not skip/retry-as-pass.

## Cases
- Same normalized class name: one class, follower validation failure.
- Duplicate instructor assignment and student enrollment: same retained row.
- Remove instructor before enrollment: follower denied. Reverse order: enrollment retained, access lost after removal.
- Archive before enrollment: follower denied. Reverse order: enrollment retained, class hidden from instructor after archive.
- Deactivate instructor before write: follower denied after lock/current-account check. Reverse order: existing write retained, subsequent access denied. This is not a concurrent sign-in/session test.
- End/re-enroll in both orders: one relationship with final state matching commit order.

## Run
With local PostgreSQL running and environment exported:
```sh
python manage.py test apps.classrooms.test_concurrency --settings=config.settings.ci --verbosity=2
python manage.py test --settings=config.settings.ci
ruff check .
```

SQLite fast tests skip this class; those skips are not PostgreSQL evidence. CI asserts PostgreSQL and discovers these tests through its existing full-suite step. Do not use CI settings for browser accounts/server. No schema/migration changes in this increment.

## Still open
Real owner/shared-instructor browser/MFA/CSRF/session acceptance (CLASSROOMS_UI.md), all possible schedules, arbitrary ORM writes, user organization/role transfers, E05 invitation races, sustained load, other-organization throughput and production operations. Record actual revision/backend/output separately from authored tests; never infer counts or claim execution from code presence.
