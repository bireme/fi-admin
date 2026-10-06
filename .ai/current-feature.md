# Current Feature: Django Upgrade Phase 5.1 — Keep `jsonfield`

## Status

In Progress

## Goals

- `jsonfield==3.2.0` stays; **no** migration to native `models.JSONField`; `src/utils/fields.py` left unchanged; storage stays TEXT
- `makemigrations --check --dry-run` reports no changes to any JSONField column (via a Makefile target)
- Tests that save and reload a model with a `utils.fields.JSONField` for list, dict, `None` and `''` values, asserting the round-trip result
- Test that the form field renders as a hidden input with class `jsonfield` and serializes without indentation/newlines (`indent=None`)
- Those tests pass on the current image (Python 3.12) **and** under Python 3.14; if they fail on 3.14, record the decision to target `python:3.13-alpine` in plan task 5.2
- Plan `001-upgrade-django-to-5.2.md` task 5.1 checkboxes updated (PyPI watch item left open with the date checked), and a log written in `.ai/logs/`

## Notes

- Source: plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md), section "5.1 — Keep `jsonfield`" (decision 2026-09-28, continues task 4.1)
- Branch: `feature/django-upgrade-phase-5.1-keep-jsonfield` (from `main`, which already contains `setup/django-5.2`). Django stays on 4.2.x; the Python 3.14 image switch itself is task 5.2 (out of scope here except for a throwaway test run)
- JSONField is used in models of `biblioref`, `leisref`, `oer`, `multimedia`, `title`, `related`, plus `biblioref/forms.py`, `api/tastypie_custom.py` and `utils/templatetags/app_filters.py`
- `dumps_for_display()` returns `None` for `None`/`'null'`/`''`, JSON-dumps lists, and returns strings unchanged — tests should cover these branches
- No existing tests reference JSONField directly
- Running under 3.14 needs a temporary image (e.g. a build arg for the base Python version, or a one-off Makefile target); keep any new command in the Makefile
- PyPI checked 2026-10-06: jsonfield 3.2.0 still latest (declares up to 3.13, marked Inactive), but tests pass on 3.14 + Django 5.2.18 via `make dev_test_py`
- Log: [2026-10-06-keep-jsonfield-phase5.1.md](.ai/logs/2026-10-06-keep-jsonfield-phase5.1.md)
- Out of scope: the Django 5.2 bump, other dependency bumps, and changing the Dockerfile base image permanently

## Detailed Plan

[019-keep-jsonfield-django-5.2.md](.ai/plans/019-keep-jsonfield-django-5.2.md) (implements task 5.1 of [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md))

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
