# Current Feature: Django Upgrade Phase 2 — Deprecation Fixes

## Status

In Progress

## Goals

- Replace all `ugettext_lazy` / `ugettext` with `gettext_lazy` / `gettext` across 72 files
- Remove `django.utils.six`, `force_text`, and unused `smart_text` imports
- Replace abandoned `django-form-utils` with minimal shim in `utils/betterforms.py`
- Remove dead `recaptcha-client` dependency from requirements.txt
- Remove `default_app_config` from `utils/__init__.py`
- Full test suite passes with no new deprecation warnings
- All changes backward-compatible with Django 2.2

## Notes

- Task 2.3 (`from_db_value` context parameter fix) is **deferred to Phase 3** — will be done when Django is upgraded to 3.2
- Branch: `upgrade-django/deprecations` from `main`
- Spec: `.ai/features/003-upgrade-django-phase2-deprecation-fixes.md`

## Detailed plan

- `.ai/plans/001-upgrade-django-to-5.2.md` (Phase 2 section)
- `.ai/features/003-upgrade-django-phase2-deprecation-fixes.md` (detailed spec)

## History

- 2026-04-13: Completed "Add indexed_database filter to LeisRef API" — filter legislation by database acronym via ?indexed_database param
- 2026-04-14: Completed "Add User-Agent header to EmailModelBackend" — hardcoded `fi-admin/2.3` UA in `src/biremelogin/authenticate.py` to avoid proxy blocks
- 2026-05-27: Starting "Django Upgrade Phase 2 — Deprecation Fixes" — following spec [003-upgrade-django-phase2-deprecation-fixes.md](.ai/features/003-upgrade-django-phase2-deprecation-fixes.md)
