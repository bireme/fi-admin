# Current Feature: Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations

## Status

In Progress

## Goals

- **5.4 — Django 5.x breaking changes** reviewed in code (tests don't cover them) and fixed where needed:
  - Password hashers: `MD5PasswordHasher` kept (still in 5.2); later switch to `PBKDF2PasswordHasher` with MD5 fallback documented
  - Forms: div-based default rendering (5.0) checked in templates using `{{ form }}` / `{{ form.as_table }}` and the biblioref `BetterModelForm` fieldsets
  - No positional-arg `Model.save(True, …)` calls left (5.1 deprecation)
  - No `index_together` left, including old migrations (converted to `indexes`)
  - No removed APIs: `assertQuerysetEqual`, `length_is`, `django.utils.timezone.utc`, `pytz`, `get_storage_class`, old `assertFormError` signature
  - Settings: `USE_L10N` / `DEFAULT_FILE_STORAGE` / `STATICFILES_STORAGE` not set (`STORAGES` if needed)
  - `DisableMigrations` in test settings still works
- **5.5 — django-tastypie 0.15.1** on Django 5.2: `src/api/tests.py` passes and a manual GET on every resource works; if anything breaks, prefer a local patch/monkeypatch in `api/`, then a fork (DRF migration out of scope)
- **5.6 — Migrations and test**:
  - `makemigrations --check` yields only no-op migrations (committed, as in Phase 4)
  - `make dev_test` with coverage, compared against the 55% baseline
  - `python manage.py rebuild_index` (Haystack 3.4.0) runs without errors
- Verification items from the plan ticked where checkable locally (login/POST logout, admin/Rosetta/TinyMCE/DeCS popup load, `check --deploy`); items needing production data or a prod-like deploy recorded as pending
- Plan `001-upgrade-django-to-5.2.md` tasks 5.4–5.6 ticked with dates/results, and a log written in `.ai/logs/`

## Notes

- Source: plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md), sections "5.4 — Fix Django 5.x breaking changes", "5.5 — Handle `django-tastypie` compatibility", "5.6 — Migrations and test" and the Phase 5 "Verification" list
- Builds on 5.2/5.3 (branch `feature/django-upgrade-phase-5.2-5.3`, commit `39b95b46`): Python 3.14.8 + Django 5.2.18, `make dev_test` green (247 tests, 5 skipped) — no test failures caused by Django 5.2, so 5.4 is mostly a code audit
- Logout via GET (5.4) was already done in 5.0 (`menu.html` POST form + `main.tests.LogoutTest`)
- Dev DB is MyISAM: `atomic()` rollbacks don't undo writes; keep this in mind for manual checks and `rebuild_index`
- Decisions 2026-10-06: `rebuild_index` will be checked manually by the user after implementation (shared test Solr); the `{{ form }}` div rendering is kept unless the visual check shows breakage
- Out of scope: switching the password hasher (plan only), DRF migration, JSONField round-trip against production data copy, prod deployment test and performance comparison (record as pending)
- Use Makefile targets for all build/test/manage commands (add new ones if needed, e.g. for `makemigrations --check`, coverage, `rebuild_index`, `check --deploy`)
- Result 2026-10-06: audit found no 5.x breaking changes left except `title.Mask.save(self)` not forwarding args (fixed + `MaskTest`); tastypie 0.15.1: 53 API tests OK and every resource GET → 200, no patch needed; `makemigrations --check` no changes; coverage 60% (249 tests, 5 skipped) vs 55% baseline; `check --deploy` no errors, only proxy/dev warnings
- Pending manual checks by the user: `rebuild_index`, browser smoke (select-document-type div form, biblioref fieldsets, admin, Rosetta, TinyMCE, DeCS popup, login/logout); new risk: `deform` needs `pkg_resources` (setuptools unpinned, 80.10.2)
- Log: [2026-10-06-django-5.2-breaking-changes-phase5.4-5.6.md](.ai/logs/2026-10-06-django-5.2-breaking-changes-phase5.4-5.6.md)

## Detailed Plan

[021-django-5.2-breaking-changes-tastypie-migrations.md](.ai/plans/021-django-5.2-breaking-changes-tastypie-migrations.md) (implements tasks 5.4–5.6 of [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md))

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
- 2026-10-06: Phases 5.2 & 5.3 "Python 3.14 + Django 5.2 dependency bumps" implemented; commit `39b95b46` on `feature/django-upgrade-phase-5.2-5.3` (not yet merged)
- 2026-10-06: Loaded "Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) tasks 5.4–5.6
- 2026-10-06: Starting "Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations" — following plan [021-django-5.2-breaking-changes-tastypie-migrations.md](.ai/plans/021-django-5.2-breaking-changes-tastypie-migrations.md)
