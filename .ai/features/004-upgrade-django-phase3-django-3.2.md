# Phase 3: Django 2.2 → 3.2 LTS (Python 3.7 → 3.10)

## Goal

First major Django version jump: 2.2.24 → 3.2.25 LTS, with Python 3.7.8 → 3.10 and all third-party packages bumped to the **newest version that supports Django 3.2** (latest-compatible strategy, to reduce work in Phases 4–5).

## Branch

`rc/3.2` — already created, contains the Phase 2 commit (`4ee052a`). The PR to `main` will carry Phase 2 + Phase 3 together (user decision).

## Decisions Made (interview 2026-07-17)

- **Branch**: work on existing `rc/3.2` (not `rc/2.6` from the plan's table); its PR bundles the unmerged Phase 2 commit
- **Dependency strategy**: latest version compatible with Django 3.2 (not the plan's conservative targets), including `requirements-dev.txt`
- **Python**: jump straight to **3.10** (Django 3.2's max), skipping 3.9 — removes the Dockerfile change from Phase 4
- **Verification**: automated tests only (`make dev_test` in the rebuilt image); manual checks happen later in the validation environment

## Pre-verified Facts (codebase exploration)

- Plan task 3.4 (`EXPOSE_API_ONLY` settings bug) is **already fixed** at `src/fi-admin/settings.py:293` — no work needed
- No leftover `ugettext` / `six` / `force_text` / `NullBooleanField` / `django.conf.urls.url` / `is_safe_url` / `Signal(providing_args)` — Phase 2 was thorough, and all URL confs already use `django.urls`
- Custom middleware (`src/utils/middleware.py`) already uses new-style `get_response` — no change needed
- Test DB is SQLite when running tests (`settings.py:390-397`); test runner is `run_tests.sh` looping over 13 apps
- Cache backend comes from env var `CACHE_BACKEND` (conf files use `memcached.MemcachedCache` — deprecated in Django 3.2, removed in 4.1)

## Acceptance Criteria

- [ ] `Dockerfile` on `python:3.10-alpine`, dev image builds (`make dev_build`)
- [ ] `Django==3.2.25` and all packages in `requirements.txt` / `requirements-dev.txt` at newest Django-3.2-compatible versions
- [ ] `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` added to settings (preserves integer PKs)
- [ ] `from_db_value` signature fixed in `src/utils/fields.py` (deferred task 2.3)
- [ ] `{% load staticfiles %}` → `{% load static %}` in all 11 templates
- [ ] `render_to_response` calls replaced with `render` and dead imports removed
- [ ] Cache backend switched from `python-memcached` to `pymemcache` (requirements + conf env files)
- [ ] `makemigrations` generates no unexpected migrations for local apps
- [ ] Full test suite passes: `make dev_test` in the rebuilt image
- [ ] No new deprecation warnings that would block Phase 4 (`python -Wd manage.py test`)

## Tasks

### 3.1 — Update Python version

**File**: `Dockerfile` line 2
- `FROM python:3.7.8-alpine AS base` → `FROM python:3.10-alpine AS base`
- Verify alpine build deps still suffice for mysqlclient 2.2.x / lxml 5.x (`mariadb-dev` present; may need `mariadb-connector-c-dev` and `pkgconfig` for mysqlclient ≥ 2.2)

### 3.2 — Fix Django 3.0 hard breakers (do BEFORE bumping Django)

All of these are backward-compatible with 2.2, so tests still run at each step.

**a) `from_db_value` signature** — `src/utils/fields.py:78`
- `def from_db_value(self, value, expression, connection, context):` → `def from_db_value(self, value, expression, connection):`

**b) `{% load staticfiles %}` → `{% load static %}`** — 11 templates:
`src/templates/{404,403,500,base,maintenance,modal_log,api_doc}.html`, `src/templates/authentication/login.html`, `src/templates/suggest/{thanks,invalid-link}.html`, `src/templates/dashboard/index.html`

**c) `render_to_response` (removed in 3.0)**
- Real calls → convert to `render(request, ...)`: `src/oer/views.py:387`, `src/utils/views.py:268` and `:323`
- Remove unused imports in: `src/biblioref/views.py`, `src/institution/views.py`, `src/thesaurus/views.py`, `src/title/views.py`, `src/leisref/views.py`
- Do NOT touch `self.render_to_response(...)` — that's the CBV mixin method, still valid

### 3.3 — Update dependencies (latest Django-3.2-compatible)

Exact pins to be confirmed against PyPI classifiers/changelogs at implementation time. Expected targets:

| Package | From | Target | Notes |
|---------|------|--------|-------|
| Django | 2.2.24 | 3.2.25 | Final 3.2 LTS release |
| mysqlclient | 1.4.6 | 2.2.x | Needs Python ≥3.8; check alpine build deps |
| django-tastypie | 0.14.3 | newest supporting 3.2 | 0.14.7 known-good fallback; verify newer |
| django-haystack | 2.8.1 | 3.3.0 | Supports Django 3.2–4.2 |
| django-rosetta | 0.9.4 | newest supporting 3.2 | ~0.10.x |
| django-tinymce | 3.0.2 | newest supporting 3.2 | |
| django-multiselectfield | 0.1.12 | latest | |
| django-crum | 0.7.8 | 0.7.9+ | |
| elastic-apm | 6.2.2 | latest 6.x | |
| gunicorn | 20.1.0 | latest | Django-agnostic |
| requests | 2.24.0 | latest | |
| pysolr | 3.9.0 | latest | |
| lxml | 4.6.3 | latest | |
| defusedxml / cssselect / simplejson / short-url / colander / deform | — | latest | Django-agnostic |
| python-memcached | 1.59 | **replace with pymemcache** | See task 3.5 |
| jsonfield | 3.1.0 | **keep** | Native JSONField migration is Phase 4 (task 4.1) |

**requirements-dev.txt**:

| Package | From | Target |
|---------|------|--------|
| django-debug-toolbar | 2.2 | newest supporting 3.2 (4.x line) |
| model-bakery | 1.3.3 | newest supporting 3.2 |
| requests_mock | 1.8.0 | latest |
| coverage | 5.5 | latest |

### 3.4 — Add `DEFAULT_AUTO_FIELD` to settings

**File**: `src/fi-admin/settings.py`
- Add `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'`
- Prevents Django 3.2 auto-migrating all PKs to BigAutoField

### 3.5 — Switch memcached client to pymemcache

- `requirements.txt`: `python-memcached==1.59` → `pymemcache` (latest)
- Conf env files: `CACHE_BACKEND=django.core.cache.backends.memcached.MemcachedCache` → `...memcached.PyMemcacheCache` in `conf/app-env`, `conf/app-env-TEMPLATE`, `conf/app-env-dev`, `conf/app-env-api`
- `PyMemcacheCache` is new in Django 3.2; `MemcachedCache` is deprecated in 3.2 and removed in 4.1 — doing this now avoids a Phase 4 breaker

### 3.6 — Bump Django and run migrations check

- Set `Django==3.2.25`, rebuild image (`make dev_build`)
- `python manage.py makemigrations` — expect NO migrations for local apps (DEFAULT_AUTO_FIELD preserves AutoField); investigate any that appear
- `python manage.py migrate` on the dev database — no errors

### 3.7 — Fix new deprecation warnings

- Run `python -Wd manage.py test` (or via `make dev_test_app`)
- Fix warnings that become errors in Django 4.x where cheap; log the rest for Phase 4

## Implementation Order

1. Task 3.2 (breaker fixes — still on Django 2.2, run `make dev_test` to confirm green)
2. Task 3.4 (`DEFAULT_AUTO_FIELD`) + Task 3.5 (pymemcache conf)
3. Task 3.1 (Dockerfile → 3.10) + Task 3.3 + 3.6 (all version bumps, rebuild, migrate check)
4. Task 3.7 (deprecation sweep)
5. Full `make dev_test` — all 13 apps green
6. Log in `.ai/logs/`, PR `rc/3.2` → `main` (carries Phase 2 commit too)

## Risks

- **django-tastypie**: newest release may not declare Django 3.2 support — fall back to 0.14.7
- **haystack 2.8 → 3.3**: major bump; 8 search_index files — API is stable but watch for import changes; Solr not exercised by tests (automated-tests-only verification accepts this gap)
- **mysqlclient 2.2.x on alpine**: build-dep changes (`pkgconfig`, `mariadb-connector-c-dev`) may be needed
- **Python 3.7 → 3.10**: stdlib removals (e.g. `collections` ABC aliases) may surface in old code or pinned deps at import time — caught by test run
