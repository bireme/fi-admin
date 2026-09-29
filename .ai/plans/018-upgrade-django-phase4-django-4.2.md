# Plan: Django Upgrade Phase 4 — Django 3.2 → 4.2 LTS (Python 3.10 → 3.12)

## Context

Phase 4 of the staged Django 5.2 upgrade (`.ai/plans/001-upgrade-django-to-5.2.md`). Phase 3 (Django 3.2, Python 3.10) is merged to `main` as `c0ba51a`. This phase jumps to the next LTS: Django 4.2.x with Python 3.12. All decisions were settled in the 2026-08-26 spec interview (`.ai/features/005-upgrade-django-phase4-django-4.2.md`): the native-JSONField migration is **dropped** (jsonfield 3.2.0 officially supports Django 4.2–5.2), MySQL 8+ in prod makes the 5.7 drop a non-issue, and verification is automated tests only.

Codebase state verified today: `Dockerfile:2` is `python:3.10-alpine`; `requirements.txt` has `Django==3.2.25`, `django-rosetta==0.9.9`, `jsonfield==3.1.0`; `settings.py:77` has `USE_L10N = True`, `settings.py:400` has `TEMPLATE_DEBUG = False`. PyPI today: Django 4.2 line is at **4.2.30**, jsonfield at **3.2.0**, django-rosetta at **0.10.3** (declares Django 4.2/5.0, Python 3.12 — good).

## Branch

Create `setup/django-4.2` from `main`.

## Steps

### 1. Version bumps (tasks 4.1 + 4.2)

- `Dockerfile:2`: `FROM python:3.10-alpine AS base` → `FROM python:3.12-alpine AS base`
- `requirements.txt`:
  - `Django==3.2.25` → `Django==4.2.30`
  - `jsonfield==3.1.0` → `jsonfield==3.2.0`
  - `django-rosetta==0.9.9` → `django-rosetta==0.10.3`
- `requirements-dev.txt`: no changes required (all pins already 4.2-compatible)
- Rebuild: `make dev_build` — watch for setuptools/build issues on Python 3.12 (no known blockers)

### 2. Settings cleanup — AFTER the Django bump (task 4.3)

`src/fi-admin/settings.py`:
- Remove `USE_L10N = True` (line 77, with its comment) — safe only once on 4.2, where `True` is the default; on 3.2 the default is `False`
- Remove `TEMPLATE_DEBUG = False` (line 400, test block) — dead setting
- `DisableMigrations` already returns `None` — no change

### 3. Verification (task 4.4)

- `make dev_makemigrations` — expect **no** local-app migrations; investigate any that appear
- `make dev_migrate` — clean run on the dev database
- `make dev_test` — full suite green (JSONField behavior covered by biblioref/oer/leisref tests)
- Deprecation sweep with `python -Wd` (add a Makefile target if needed, per CLAUDE.md): capture remaining Django 5.x deprecation warnings

### 4. Wrap-up

- Log summary + Phase 5 deprecation list in `.ai/logs/2026-08-27-upgrade-django-4.2.md`
- Save this plan as `.ai/plans/018-upgrade-django-phase4-django-4.2.md` and link it in `.ai/current-feature.md`
- PR `setup/django-4.2` → `main` (no Co-Authored-By trailer)

## Risks

- **jsonfield 3.1.0 → 3.2.0**: serialization changes would surface in JSONField-heavy app tests
- **rosetta 0.10.3**: not test-covered; manual check deferred to validation environment
- **SQLite-only tests**: MySQL 8 behavior proven only in validation (accepted gap, same as Phase 3)

## Acceptance criteria

Mirrors the spec: image builds on 3.12-alpine; Django 4.2.30/jsonfield 3.2.0/rosetta 0.10.3 installed; `USE_L10N`/`TEMPLATE_DEBUG` gone; no unexpected migrations; `make dev_test` green; deprecations logged for Phase 5.
