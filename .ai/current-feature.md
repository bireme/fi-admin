# Current Feature: Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps

## Status

In Progress

## Goals

- `Dockerfile` default `ARG PYTHON_VERSION` changed from `3.12` to `3.14`; dev and prod images build on `python:3.14-alpine` (task 5.2)
- `Django` bumped from 4.2.30 to the latest 5.2.x (≥ 5.2.8, needed for Python 3.14)
- Remaining packages in the 5.3 table bumped to Django 5.2 / Python 3.14 compatible versions, **one at a time** with `make dev_test` after each:
  - `django-haystack` 3.3.0 → 3.4.0 / latest (confirm 5.2 support)
  - `django-tinymce` 4.1.0 → 5.0.0
  - `model-bakery` (dev) 1.17.0 → latest 1.x (1.24.2)
  - `mysqlclient` stays 2.2.8 (already latest 2.2.x); `lxml` 6.1.1 → 6.1.3
  - `django-rosetta` 0.10.3 and `django-multiselectfield` 1.0.1 have no newer release → keep, smoke-test
- `jsonfield==3.2.0`, `django-tastypie==0.15.1` and `django-debug-toolbar==5.2.0` stay as they are
- `make dev_test` on Python 3.14 + Django 5.2 shows no failures beyond the Django-5.2 baseline; baseline failures (task 5.4 breaking changes) are **recorded, not fixed** (decided 2026-10-06)
- Plan `001-upgrade-django-to-5.2.md` tasks 5.2/5.3 updated with the final versions and dates, and a log written in `.ai/logs/`

## Notes

- Source: plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md), sections "5.2 — Update Python version" and "5.3 — Update dependency versions"
- Builds on 5.1 (branch `feature/django-upgrade-phase-5.1-keep-jsonfield`, commit `b50cc6c3`), which added `ARG PYTHON_VERSION` to the `Dockerfile` and `make dev_test_py PY=…`, and confirmed the image (incl. mysqlclient/lxml) builds on 3.14 with utils tests passing on Django 5.2.18
- The 5.3 table targets / 5.1 PyPI-watch tick were committed as `45e8f1dc`; `feature/django-upgrade-phase-5.2-5.3` branches off 5.1 (PR #1579), so its PR stacks on 5.1
- Version pins live in `requirements.txt` and `requirements-dev.txt`
- Out of scope: task 5.4 breaking-change fixes (forms rendering, `index_together`, removed APIs, settings) beyond what's needed to make the test suite pass; 5.5 tastypie manual checks; 5.6 migrations/`rebuild_index`/coverage comparison — note any blockers found for those tasks
- Use Makefile targets for all build/test commands (add new ones if needed)
- Result 2026-10-06: Python 3.14.8 + Django 5.2.18, `make dev_test` fully green (247 tests, 5 skipped); the only Django-5.2 baseline errors (3 in biblioref) came from model-bakery 1.17.0 and were fixed by 1.24.2; `django-multiselectfield` turned out to be imported but unused
- Log: [2026-10-06-python-3.14-django-5.2-deps-phase5.2-5.3.md](.ai/logs/2026-10-06-python-3.14-django-5.2-deps-phase5.2-5.3.md)

## Detailed Plan

[020-upgrade-python-3.14-django-5.2-deps.md](.ai/plans/020-upgrade-python-3.14-django-5.2-deps.md) (implements tasks 5.2 and 5.3 of [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md))

## History

- 2026-04-13: Completed "Add indexed_database filter to LeisRef API" — filter legislation by database acronym via ?indexed_database param
- 2026-04-14: Completed "Add User-Agent header to EmailModelBackend" — hardcoded `fi-admin/2.3` UA in `src/biremelogin/authenticate.py` to avoid proxy blocks
- 2026-05-27: Starting "Django Upgrade Phase 2 — Deprecation Fixes" — following spec [003-upgrade-django-phase2-deprecation-fixes.md](.ai/features/003-upgrade-django-phase2-deprecation-fixes.md)
- 2026-07-17: Completed "Django Upgrade Phase 2 — Deprecation Fixes" — merged into `rc/3.2` flow; commit `4ee052a`
- 2026-07-17: Starting "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — following spec [004-upgrade-django-phase3-django-3.2.md](.ai/features/004-upgrade-django-phase3-django-3.2.md)
- 2026-08-27: Completed "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — merged to `main`; commit `c0ba51a`
- 2026-08-27: Starting "Django Upgrade Phase 4 — Django 3.2 → 4.2 LTS" — following plan [018-upgrade-django-phase4-django-4.2.md](.ai/plans/018-upgrade-django-phase4-django-4.2.md)
- 2026-09-28: Phase 4 "Django 3.2 → 4.2 LTS" implemented; commit `5d2e234a` is on `validation` (not yet merged to `main`)
- 2026-09-28: Loaded "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — following spec [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
- 2026-09-28: Starting "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" on `setup/django-5.2` — following spec [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
- 2026-10-06: Completed "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — merged to `main` (PR #1578); commit `cf369f75`
- 2026-10-06: Loaded "Django Upgrade Phase 5.1 — Keep jsonfield" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) task 5.1
- 2026-10-06: Starting "Django Upgrade Phase 5.1 — Keep jsonfield" — following plan [019-keep-jsonfield-django-5.2.md](.ai/plans/019-keep-jsonfield-django-5.2.md)
- 2026-10-06: Loaded "Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) tasks 5.2 and 5.3
- 2026-10-06: Starting "Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps" — following plan [020-upgrade-python-3.14-django-5.2-deps.md](.ai/plans/020-upgrade-python-3.14-django-5.2-deps.md)
