# Plan 021: Django Upgrade Phases 5.4, 5.5 & 5.6 — breaking-change audit, tastypie checks, migrations

> Implements tasks 5.4–5.6 of [001-upgrade-django-to-5.2.md](001-upgrade-django-to-5.2.md)

## Context

Phases 5.2/5.3 (commit `39b95b46`) moved the app to Python 3.14.8 + Django 5.2.18, and `make dev_test` is green (247 tests, 5 skipped). The remaining Phase 5 tasks are a code review of Django 5.x breaking changes that tests don't cover (5.4), checking tastypie 0.15.1 on 5.2 (5.5), and migrations/coverage/index checks (5.6). The aim is to close those checkboxes in plan `001` with evidence, fixing only what's actually broken.

## Pre-audit findings (done during planning, 2026-10-06)

| Check | Result |
|---|---|
| `index_together` | none in `src/` (incl. migrations) ✅ |
| Positional `save(True, …)` | none ✅ |
| `assertQuerysetEqual`, `length_is`, `pytz`, `get_storage_class`, `assertFormError` | none ✅ |
| `timezone.utc` | only `biblioref/tests.py:22`, and it's the stdlib `datetime.timezone` → fine ✅ |
| `USE_L10N` / `DEFAULT_FILE_STORAGE` / `STATICFILES_STORAGE` | not set ✅ |
| `PASSWORD_HASHERS` | MD5 only (`fi-admin/settings.py:261`); MD5 still exists in 5.2 → keep |
| `DisableMigrations` (`settings.py:394`) | still works (test suite runs with it) ✅ |
| `{{ form }}` | only `templates/biblioref/select_document_type.html:28` → div rendering now |
| `title/models.py:287` `Mask.save(self)` | takes no args → would break `save(update_fields=…)` / `save(using=…)`; harden to `save(self, *args, **kwargs)` |
| `run_coverage.sh` | omits the `api` app that `run_tests.sh` includes |

## Steps

### 1. Makefile targets (CLAUDE.md: everything through make)
Add the following to `Makefile`, next to the existing `dev_*` targets:
- `dev_check_deploy`: `python manage.py check --deploy`
- `dev_update_index`: `python manage.py update_index $(args)`, for the manual Haystack check

Reuse the existing `dev_makemigrations_check`, `dev_test`, `dev_test_app` and `dev_test_coverage` targets.

### 2. Task 5.4 — fixes from the audit
- `src/title/models.py`: change `Mask.save(self)` to `save(self, *args, **kwargs)` and pass the args through to `super().save(*args, **kwargs)`. Add a small test in `title/tests.py` that calls `save(update_fields=[...])` on a `Mask`.
- `src/run_coverage.sh`: add `api` to `APPS` so coverage matches `run_tests.sh`.
- Password hasher: no code change. Add a note to plan `001` 5.4 describing the later switch: `PBKDF2PasswordHasher` first, with MD5 kept as a fallback so hashes upgrade on login.
- Forms: open `/bibliographic/new/` (select document type) in the browser after `make dev_up` and check the div-rendered form. **Keep the divs** unless the layout is broken. Also open one biblioref edit form to check the `BetterModelForm` fieldsets render.

### 3. Task 5.5 — tastypie
- `make dev_test_app app=api`: all 53 API tests pass.
- Manual GET on every resource registered in `src/api/urls.py` (12 `path('')` resources, plus descriptors/qualifiers/desc/qualif/ths and the index endpoints) with `?format=json&limit=1` via `make dev_exec cmd="python -c …"` or curl against the dev server. Record status codes in the log.
- Only if something breaks: add a local patch in `src/api/tastypie_custom.py`.

### 4. Task 5.6 — migrations and coverage
- `make dev_makemigrations_check`. If it reports changes, inspect them. If they're no-ops (`AlterField` choices/help text, etc.), generate them with `make dev_makemigrations` and commit them, as in Phase 4.
- `make dev_test_coverage`: record the overall % and compare it per app with the 55% baseline (`.ai/logs/2026-04-08-baseline-coverage-report.md`).
- `rebuild_index`: **the user will check this manually afterwards** against the test Solr. Add `dev_update_index` as the helper and leave the 5.6 checkbox open with a note.

### 5. Verification list checks (local)
- `make dev_check_deploy`: record the warnings. Expect the HSTS/SSL/secure-cookie warnings that prod handles at the proxy. Don't change the settings unless a warning is new in 5.x.
- In the browser: login, POST logout, admin index, Rosetta, TinyMCE editor on a form, DeCS popup.
- Leave open with a note: JSONField round-trip on a copy of prod data, `make prod_migrate` on a prod-like deploy, the performance comparison, and `rebuild_index` (manual).

### 6. Docs
- Plan `001`: tick the 5.4/5.5/5.6 items and Verification items with date and result. Update the Risk Registry rows for tastypie and haystack.
- Write the log `.ai/logs/2026-10-06-django-5.2-breaking-changes-phase5.4-5.6.md`.
- Update `current-feature.md` notes with the results.

## Critical files
- `Makefile`
- `src/title/models.py`, `src/title/tests.py`
- `src/run_coverage.sh`
- `src/templates/biblioref/select_document_type.html` (only if the visual check fails)
- `src/api/tastypie_custom.py` (only if a resource breaks)
- `.ai/plans/001-upgrade-django-to-5.2.md`, `.ai/current-feature.md`, `.ai/logs/…`

## Verification
- `make dev_test` is green (≥ 248 tests including the new Mask test)
- `make dev_test_app app=api` passes, and the manual resource GETs return 200
- `make dev_makemigrations_check` reports "No changes detected" (after committing any no-op migrations)
- `make dev_test_coverage` reports an overall % ≥ the 55% baseline
- `make dev_check_deploy` shows no Django-5.x-specific errors
- Browser smoke test passes (login/logout, admin, Rosetta, TinyMCE, DeCS popup, select-document-type form)
