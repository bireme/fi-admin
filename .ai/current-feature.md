# Current Feature: Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS (Python 3.10)

## Status

In Progress

## Goals

- Upgrade Django 2.2.24 → 3.2.25 LTS with Python 3.7.8 → 3.10 (`python:3.10-alpine`)
- Bump all packages (prod + dev) to newest versions compatible with Django 3.2 (latest-compatible strategy)
- Fix Django 3.0 hard breakers before the bump: `from_db_value` signature, `{% load staticfiles %}` in 11 templates, `render_to_response` calls/imports in 7 views files
- Add `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` to settings (preserve integer PKs)
- Switch `python-memcached` → `pymemcache` (`PyMemcacheCache`) in requirements and conf env files
- `makemigrations` produces no unexpected migrations for local apps
- Full test suite passes: `make dev_test` in the rebuilt Python 3.10 image (automated tests only — manual checks deferred to validation environment)

## Notes

- Branch: `rc/3.2` (already exists, contains Phase 2 commit `4ee052a`); PR to `main` bundles Phase 2 + Phase 3
- Plan task 3.4 (`EXPOSE_API_ONLY` bug) already fixed at `src/fi-admin/settings.py:293` — no work needed
- `jsonfield==3.1.0` stays — native JSONField migration is Phase 4
- django-tastypie fallback if latest doesn't support 3.2: `0.14.7`
- Spec: `.ai/features/004-upgrade-django-phase3-django-3.2.md`

## Detailed plan

- `.ai/plans/001-upgrade-django-to-5.2.md` (Phase 3 section)
- `.ai/features/004-upgrade-django-phase3-django-3.2.md` (detailed spec with implementation order)

## History

- 2026-04-13: Completed "Add indexed_database filter to LeisRef API" — filter legislation by database acronym via ?indexed_database param
- 2026-04-14: Completed "Add User-Agent header to EmailModelBackend" — hardcoded `fi-admin/2.3` UA in `src/biremelogin/authenticate.py` to avoid proxy blocks
- 2026-05-27: Starting "Django Upgrade Phase 2 — Deprecation Fixes" — following spec [003-upgrade-django-phase2-deprecation-fixes.md](.ai/features/003-upgrade-django-phase2-deprecation-fixes.md)
- 2026-07-17: Completed "Django Upgrade Phase 2 — Deprecation Fixes" — merged into `rc/3.2` flow; commit `4ee052a`
- 2026-07-17: Starting "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — following spec [004-upgrade-django-phase3-django-3.2.md](.ai/features/004-upgrade-django-phase3-django-3.2.md)
