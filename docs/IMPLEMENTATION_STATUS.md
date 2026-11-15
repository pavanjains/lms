# First implementation slice

All entries are authored artifacts, not externally merged tickets.

| Ticket | Status | Notes |
|---|---|---|
| E01-01 | Implemented; runtime verification pending | Django project and entrypoints |
| E01-02 | Partial | Core, accounts, organizations modules; remaining feature modules deferred |
| E01-03 | Partial | Dependency ranges authored; resolved lockfile not generated |
| E01-04 | Implemented; runtime verification pending | Development, test, PostgreSQL CI, production settings |
| E01-05 | Configured; unverified | Local PostgreSQL Compose; not started here |
| E01-06 | Partial | Ruff lint configured; formatter checks deferred until formatter can run |
| E01-07 | Configured; unverified | PostgreSQL CI checks, migrations, tests |
| E01-08 | Draft | Setup guide included; independent setup not demonstrated |
| E02-01 | Draft | Decision register included |
| E02-02–04 | Implemented; runtime verification pending | Organization, custom user, student profile, initial migrations |
| E03-01 | Partial | Minimal semantic layout, no role navigation or full styling |

No ticket is marked DONE without its acceptance evidence. No login, MFA, account management UI, class permissions, lessons, assignments, or private uploads are implemented in this slice.

Validation performed here: Python syntax parsing and artifact integrity only. Django runtime tests, migrations, Docker services, PostgreSQL constraints, Ruff, and CI require execution in the target environment.

Next: resolve dependencies to a reviewed lockfile; run CI; implement owner bootstrap and staff MFA before protected features; then classes and authorization.
