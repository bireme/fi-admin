# Current Feature: Django Upgrade Phase 4 — Django 3.2 → 4.2 LTS (Python 3.12)

## Status

In Progress

## Goals

- Upgrade Django 3.2.25 → 4.2.x (latest patch) LTS with Python 3.10 → 3.12 (`python:3.12-alpine`)
- Bump the two Django-pinned outliers: `jsonfield` 3.1.0 → 3.2.0, `django-rosetta` 0.9.9 → newest 4.2-compatible (0.10.x+)
- Remove `USE_L10N = True` and the dead `TEMPLATE_DEBUG = False` from settings — **after** the Django bump
- `makemigrations` produces no unexpected migrations for local apps; `make dev_migrate` runs clean
- Full test suite passes: `make dev_test` in the rebuilt Python 3.12 image (automated tests only — manual checks deferred to validation environment)
- JSONField behavior unchanged after the jsonfield bump (covered by biblioref/oer/leisref tests)
- Remaining Django 5.x deprecation warnings (`python -Wd manage.py test`) logged to `.ai/logs/` for Phase 5

## Notes

- Branch: `setup/django-4.2`, created from `main` (already contains Phase 3 commit `c0ba51a`)
- Plan task 4.1 (migrate to native `django.db.models.JSONField`) is **dropped** — jsonfield 3.2.0 declares Django 4.2–5.2 / Python 3.10–3.13, so `utils.fields.JSONField` stays on the library through Phase 5
- MySQL 5.7 drop in 4.2 is not a blocker: prod fi-admin and DeCS databases are already on MySQL 8+
- No Django 4.0/4.1 hard breakers found in code (no `conf.urls.url`, `ifequal`, `is_ajax()`, `NullBooleanField`, `pytz`, `ugettext`, `index_together`); cache is already `PyMemcacheCache`
- Most pins already support 4.2 (tastypie 0.14.7, haystack 3.3.0, tinymce 4.1.0, multiselectfield 1.0.1, crum 0.7.9, pymemcache 4.0.0, mysqlclient 2.2.8, debug-toolbar 4.3.0, model-bakery 1.17.0)
- Risks: jsonfield minor bump could shift serialization; rosetta 0.10.x has no test coverage; tests are SQLite-only so MySQL 8 behavior is proven only in validation
- Spec: `.ai/features/005-upgrade-django-phase4-django-4.2.md`

## Detailed Plan

- [018-upgrade-django-phase4-django-4.2.md](.ai/plans/018-upgrade-django-phase4-django-4.2.md) (approved 2026-08-27)
- `.ai/features/005-upgrade-django-phase4-django-4.2.md` (detailed spec with tasks 4.1–4.4 and implementation order)
- `.ai/plans/001-upgrade-django-to-5.2.md` (Phase 4 section — note the plan deviation on task 4.1)

## History

- 2026-04-13: Completed "Add indexed_database filter to LeisRef API" — filter legislation by database acronym via ?indexed_database param
- 2026-04-14: Completed "Add User-Agent header to EmailModelBackend" — hardcoded `fi-admin/2.3` UA in `src/biremelogin/authenticate.py` to avoid proxy blocks
- 2026-05-27: Starting "Django Upgrade Phase 2 — Deprecation Fixes" — following spec [003-upgrade-django-phase2-deprecation-fixes.md](.ai/features/003-upgrade-django-phase2-deprecation-fixes.md)
- 2026-07-17: Completed "Django Upgrade Phase 2 — Deprecation Fixes" — merged into `rc/3.2` flow; commit `4ee052a`
- 2026-07-17: Starting "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — following spec [004-upgrade-django-phase3-django-3.2.md](.ai/features/004-upgrade-django-phase3-django-3.2.md)
- 2026-08-27: Completed "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — merged to `main`; commit `c0ba51a`
- 2026-08-27: Starting "Django Upgrade Phase 4 — Django 3.2 → 4.2 LTS" — following plan [018-upgrade-django-phase4-django-4.2.md](.ai/plans/018-upgrade-django-phase4-django-4.2.md)
