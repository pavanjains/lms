# Robotics LMS — first implementation slice

This archive contains authored Django foundation code, not a finished LMS. See docs/IMPLEMENTATION_STATUS.md for exact scope and validation limits. Do not deploy for children or real users yet.

## Prerequisites
Python 3.12, Docker Compose, and a shell. The CI targets Python 3.12 and PostgreSQL 16; these are implementation choices pending environment verification.

## Local setup (POSIX shell)
```sh
cp .env.example .env
# Edit local values. Never commit .env.
docker compose up -d db
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
# This sample environment file contains simple shell-compatible assignments only.
set -a
. ./.env
set +a
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000/ and /health/live/. Liveness does not assert database/storage readiness. No login or admin routes are enabled. Do not run createsuperuser as a substitute for the planned owner bootstrap: organization and LMS role are required.

Django does not automatically load .env; Docker Compose does. Export the environment for host-run commands as shown above. On Windows, use equivalent environment assignment in your shell.

## Tests
Fast model/view tests using an in-memory SQLite database (not PostgreSQL acceptance evidence):
```sh
python manage.py test --settings=config.settings.test
```
PostgreSQL verification, matching CI (local DB user needs permission to create a test database):
```sh
DJANGO_SETTINGS_MODULE=config.settings.ci python manage.py test
ruff check .
```
Dependencies are range-constrained, not locked. Generate and review a resolved lockfile in the target environment before claiming reproducible installs.

## Safety and operations
- Production settings require a non-development secret and explicit allowed hosts.
- HTTPS/proxy topology, email, MFA, authorization, retention, uploads, monitoring, and backups remain unfinished.
- Framework role fields are not a complete authorization policy.
- Model clean() is not automatically called by every ORM write; use validated services for role/profile relationships.
- Student passwords use Django hashers; the fast test hasher is for tests only.
- Do not delete production records by adapting development reset commands.

## Next implementation batch
1. Execute dependency resolution, migration drift checks, and PostgreSQL CI.
2. Fix issues and record acceptance evidence.
3. Implement E04 owner bootstrap and staff authentication/MFA.
4. Implement class membership and centralized class-scoped authorization.
5. Wire student onboarding only after permission boundaries exist.
