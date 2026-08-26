# Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS (Python 3.10)

Date: 2026-07-17
Branch: `rc/3.2`
Spec: `.ai/features/004-upgrade-django-phase3-django-3.2.md`

## Summary

Upgraded fi-admin from Django 2.2.24 / Python 3.7.8 to **Django 3.2.25 LTS / Python 3.10** (skipping 3.9, straight to Django 3.2's max supported Python). All dependencies bumped to the newest versions that support Django 3.2. Full test suite green: 200 tests across 13 apps, 5 pre-existing skips in biblioref.

## Changes

### Django 3.0 breaker fixes (backward-compatible, applied before the bump)

- `src/utils/fields.py` — `from_db_value` dropped the removed `context` parameter (deferred task 2.3)
- 11 templates — `{% load staticfiles %}` → `{% load static %}` (`404/403/500/base/maintenance/modal_log/api_doc`, `authentication/login`, `suggest/thanks`, `suggest/invalid-link`, `dashboard/index`)
- `render_to_response` (removed in 3.0): real calls converted to `render(request, ...)` in `src/oer/views.py`, `src/utils/views.py` (×2); dead imports removed from biblioref, institution, thesaurus, title, leisref views
- Dead `from django.utils.functional import curry` imports removed from `src/main/views.py`, `src/events/views.py`, `src/log/middleware.py` (curry removed in Django 3.0; found at runtime, none were called)

### Settings

- Added `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` — preserves existing integer PKs, prevents BigAutoField auto-migrations
- Plan task 3.4 (`EXPOSE_API_ONLY` bug) was already fixed in a prior commit — no change needed

### Cache backend

- `python-memcached==1.59` → `pymemcache==4.0.0`
- `CACHE_BACKEND` → `django.core.cache.backends.memcached.PyMemcacheCache` in `conf/app-env`, `app-env-TEMPLATE`, `app-env-dev`, `app-env-api` (`MemcachedCache` is deprecated in 3.2, removed in 4.1)

### Dockerfile

- `FROM python:3.7.8-alpine` → `FROM python:3.10-alpine`
- Added `pkgconf` to build deps (required by mysqlclient 2.2.x)
- Removed `py-lxml` apk package (no longer exists in current Alpine; lxml installs from musllinux wheels)

### Dependencies (`requirements.txt`)

| Package | From | To |
|---------|------|-----|
| Django | 2.2.24 | 3.2.25 |
| mysqlclient | 1.4.6 | 2.2.8 |
| gunicorn | 20.1.0 | 26.0.0 |
| django-rosetta | 0.9.4 | 0.9.9 (0.10.x requires Django 4.2) |
| django-tastypie | 0.14.3 | 0.14.7 (0.15.x requires Django 4.2) |
| django-haystack | 2.8.1 | 3.3.0 |
| requests | 2.24.0 | 2.34.2 |
| pysolr | 3.9.0 | 3.11.0 |
| lxml | 4.6.3 | 6.1.1 |
| defusedxml | 0.6.0 | 0.7.1 |
| cssselect | 1.1.0 | 1.4.0 |
| simplejson | 3.17.0 | 4.1.1 |
| deform | 2.0.15 | 3.0.1 |
| django-tinymce | 3.0.2 | 4.1.0 |
| colander | 1.8.3 | 2.0 |
| django-multiselectfield | 0.1.12 | 1.0.1 |
| python-memcached | 1.59 | replaced by pymemcache 4.0.0 |
| django-crum | 0.7.8 | 0.7.9 |
| elastic-apm | 6.2.2 | 6.26.2 |
| jsonfield | 3.1.0 | kept (native JSONField migration is Phase 4) |
| short-url | 1.2.2 | kept |

### Dev dependencies (`requirements-dev.txt`)

| Package | From | To |
|---------|------|-----|
| model-bakery | 1.3.3 | 1.17.0 (1.18+ requires Django 4.2) |
| requests_mock | 1.8.0 | 1.12.1 |
| django-debug-toolbar | 2.2 | 4.3.0 (4.4+ requires Django 4.2.9) |
| coverage | 5.5 | 7.15.2 |

### Migrations

`makemigrations` generated 10 migrations (attachments, biblioref, classification, database, help, institution, oer, related, thesaurus, title). All verified with `sqlmigrate` to produce **zero SQL** — they capture years of Python-level model drift (choices lists, verbose_names, upload_to) never recorded in migrations. Kept so migration state is clean for Phases 4–5. Applied to the local dev MySQL along with Django's own `auth.0012` without errors.

### Code cleanups from deprecation sweep

Fixed 4 invalid escape sequence warnings (raw-string prefixes): `biblioref/forms.py:184`, `biblioref/views.py:62`, `leisref/models.py:578`, `leisref/search_indexes.py:65`.

## Verification

- Full suite before the bump (Django 2.2 + breaker fixes): green
- Full suite after the bump (Django 3.2.25 / Python 3.10.20): **13/13 apps OK — 200 tests, 5 pre-existing biblioref skips**
- `python -Wa manage.py test main biblioref api utils`: **zero `RemovedInDjango4X` warnings** — clean runway for Phase 4
- `manage.py migrate` on dev MySQL: no errors

## Notes / risks carried forward

- deform 3.0.1 emits a `pkg_resources` deprecation warning and pins `setuptools<81` — revisit in Phase 4/5
- TinyMCE editor JS is served from repo static files (`TINYMCE_JS_URL`), so the django-tinymce 4.x bump only affects widget rendering — verify rich-text editing in the validation environment
- Haystack/Solr indexing is not exercised by tests — verify index rebuild in the validation environment
- gunicorn 20 → 26 is a large jump — verify prod entrypoint flags on deploy

## What was done

What was done

  Upgrade landed: Django 2.2.24 → 3.2.25 LTS, Python 3.7.8 → 3.10.20, all on branch rc/3.2 (uncommitted — /feature complete handles that).

  - Breaker fixes (all applied and test-verified on 2.2 first): from_db_value signature, {% load static %} in 11 templates, render_to_response → render plus dead-import cleanup in 7 view files, and
  three dead curry imports that only surfaced at runtime on 3.2.
  - Settings/config: DEFAULT_AUTO_FIELD = AutoField (integer PKs preserved — confirmed, no BigAutoField migrations appeared); python-memcached → pymemcache 4.0.0 with PyMemcacheCache in all four
  conf env files.
  - Dependencies: everything bumped to the newest Django-3.2-compatible release. Ceilings worth knowing: tastypie 0.14.7, rosetta 0.9.9, debug-toolbar 4.3.0, model-bakery 1.17.0 — all capped
  because their next releases require Django 4.2 (they become Phase 4 bumps). Dockerfile also needed pkgconf added and the defunct py-lxml apk package removed.
  - Migrations: makemigrations did generate 10 migrations — I verified each with sqlmigrate and all produce zero SQL (they capture old Python-level model drift, not schema changes). I kept them so
  - Breaker fixes (all applied and test-verified on 2.2 first): from_db_value signature, {% load static %} in 11 templates, render_to_response → render plus dead-import cleanup in 7 view files, and
  three dead curry imports that only surfaced at runtime on 3.2.
  - Settings/config: DEFAULT_AUTO_FIELD = AutoField (integer PKs preserved — confirmed, no BigAutoField migrations appeared); python-memcached → pymemcache 4.0.0 with PyMemcacheCache in all four
  conf env files.
  - Dependencies: everything bumped to the newest Django-3.2-compatible release. Ceilings worth knowing: tastypie 0.14.7, rosetta 0.9.9, debug-toolbar 4.3.0, model-bakery 1.17.0 — all capped
  because their next releases require Django 4.2 (they become Phase 4 bumps). Dockerfile also needed pkgconf added and the defunct py-lxml apk package removed.
  - Migrations: makemigrations did generate 10 migrations — I verified each with sqlmigrate and all produce zero SQL (they capture old Python-level model drift, not schema changes). I kept them so
  migration state is clean for Phase 4, and migrate ran cleanly on the dev MySQL (mysql-local).

  Verification

  - run_tests.sh: 13/13 apps OK, 200 tests (5 pre-existing biblioref skips marked "Figure out why these tests are broken!" — unrelated to the upgrade).
  - Warnings-enabled run: zero RemovedInDjango4X warnings, so the Phase 4 runway is already clean. The only findings were 4 invalid-escape-sequence warnings, fixed with raw strings.
  - Log written to .ai/logs/2026-07-17-django-upgrade-phase3-django-3.2.md, including risks carried forward (TinyMCE UI, Solr rebuild, and gunicorn 20→26 need eyeballing in the validation
  environment — none are test-covered).


## Review — Phase 3: Django 2.2 → 3.2 LTS

### ✅ Goals met (7/7)

| Goal                                       | Evidence                                                                                                                                                                                         |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Django 3.2.25 / Python 3.10                | Verified in container: `3.10.20`, `3.2.25`                                                                                                                                                       |
| All deps at newest 3.2-compatible versions | Each pin checked against PyPI metadata; ceilings (tastypie 0.14.7, rosetta 0.9.9, ddt 4.3.0, model-bakery 1.17.0) are hard limits imposed by Django-4.2 floors upstream                          |
| Hard breakers fixed                        | `from_db_value`, 11 templates, `render_to_response` in 7 files — diffs are surgical, plus dead `curry` imports found at runtime                                                                  |
| `DEFAULT_AUTO_FIELD`                       | In settings with explanatory comment; confirmed no BigAutoField migrations generated                                                                                                             |
| pymemcache switch                          | `requirements.txt` + all 4 conf files (note: only `app-env-TEMPLATE` is git-tracked; the other three are local/gitignored, which is why they don't show in `git status` — still updated on disk) |
| No unexpected migrations                   | 10 migrations *did* appear, but each was verified via `sqlmigrate` to emit **zero SQL** (drift capture only) and applied cleanly to dev MySQL — kept deliberately                                |
| `make dev_test` green                      | 13/13 apps, 200 tests, 5 pre-existing skips; zero `RemovedInDjango4X` warnings                                                                                                                   |

### ⚠️ Code quality — no issues found

Every diff hunk is exactly the intended change; the `render()` conversions now run context processors on those three templates, which is the correct modern behavior and harmless for these simple templates.

### 🚫 Scope creep — none in the feature work, but commit hygiene needed

Three untracked files in `proc/` that I did not create (`dump-db.sh`, `dump-db-data.sh`, `fi_admin_tst_dump-20260717.sql`) plus the pre-existing `Makefile` edit (the `import2prod` path fix from before this session) are sitting in the working tree. **The `.sql` dump especially should not be committed** — it likely contains database data. The `complete` step should stage the feature files explicitly rather than `git add -A`.

### Verdict: **Ready to complete**

Run `/feature complete` when ready — I'll keep the unrelated `proc/` files and `Makefile` change out of the Phase 3 commit (or tell me if you want the Makefile fix included).
