# Phase 4: Django 3.2 → 4.2 LTS (Python 3.10 → 3.12)

## Goal

Second major Django version jump: 3.2.25 → 4.2.x (latest patch) LTS, with Python 3.10 → 3.12. The custom `utils.fields.JSONField` stays on the `jsonfield` library (bumped 3.1.0 → 3.2.0) — the plan's task 4.1 (migrate to native `django.db.models.JSONField`) is **dropped** (user decision, see below).

## Branch

`setup/django-4.2` (user decision, 2026-08-26) — created from `main`, which already contains Phase 3 (`c0ba51a`).

## Decisions Made (interview 2026-08-26)

- **jsonfield stays** (supersedes plan task 4.1): keep `utils.fields.JSONField` subclassing `jsonfield.JSONField`, bump the lib to **3.2.0**. Verified against the 3.1.0 source: it only uses modern APIs (`gettext_lazy`, `force_str`, 3-arg `from_db_value`), nothing removed in Django 4.x. 3.2.0's PyPI classifiers explicitly declare **Django 4.2–5.2 and Python 3.10–3.13**, so this also removes the Phase 5 concern — no native-JSONField migration is needed on this upgrade path
- **MySQL**: production servers for both the main fi-admin database and the DeCS database are already on **MySQL 8+** — Django 4.2's drop of MySQL 5.7 support is not a blocker; no pre-flight task needed
- **Branch**: `setup/django-4.2` (not the plan table's `rc/2.7`)
- **Verification**: automated tests only (`make dev_test` in rebuilt image), same as Phase 3; manual checks deferred to validation environment

## Pre-verified Facts (codebase exploration, 2026-08-26)

- **Phase 3 latest-compatible strategy paid off** — these pins already support Django 4.2, no bump needed: `django-tastypie==0.14.7`, `django-haystack==3.3.0`, `django-tinymce==4.1.0`, `django-multiselectfield==1.0.1`, `django-crum==0.7.9`, `pymemcache==4.0.0`, `mysqlclient==2.2.8` (also Python 3.12-ready), `django-debug-toolbar==4.3.0`, `model-bakery==1.17.0`
- **Django-pinned outliers**: `django-rosetta==0.9.9` → needs 0.10.x for the 4.2 line; `jsonfield==3.1.0` → 3.2.0
- **No Django 4.0/4.1 hard breakers in code**: zero hits for `django.conf.urls.url` (all URLconfs on `path`/`re_path`), `{% ifequal %}`, `request.is_ajax()`, `NullBooleanField`, `pytz`, `providing_args`, `force_text`/`smart_text`/`ugettext` (only a comment in `api/tests.py`), `django.utils.timezone.utc`, legacy `assertFormError` signatures, `index_together`
- **Cache backend already `PyMemcacheCache`** (Phase 3) — `MemcachedCache` removal in 4.1 is a non-issue
- **Settings** (`src/fi-admin/settings.py`): `USE_L10N = True` at line 77 (deprecated 4.0, removed 5.0 — remove it); `TEMPLATE_DEBUG = False` at line 400 in the `if 'test'` block (dead setting, remove); `DisableMigrations.__getitem__` already returns `None` (the Django 3.2+ contract — compatible as-is); no `CSRF_TRUSTED_ORIGINS`, no `DEFAULT_FILE_STORAGE`/`STATICFILES_STORAGE` overrides
- **JSONField surface** (unchanged this phase, documented for Phase 5 reference): ~25 declarations across `biblioref`, `oer`, `title`, `multimedia`, `leisref`, `related` pass `dump_kwargs={'ensure_ascii': False}`; historical migrations serialize those kwargs; `api/tastypie_custom.py:45` does `isinstance(f, JSONField)`. jsonfield 3.2.0 keeps the same `dump_kwargs`/`load_kwargs` API, so no code change expected
- Tests run on SQLite (`settings.py:404`); MySQL only in prod/validation
- No `distutils`/`imp`/`cgi` usage in the codebase (Python 3.12 stdlib removals)
- No CI workflows in the repo — verification is local via Makefile

## Acceptance Criteria

- [ ] `Dockerfile` on `python:3.12-alpine`, dev image builds (`make dev_build`)
- [ ] `Django==4.2.x` (latest patch), `jsonfield==3.2.0`, `django-rosetta` at newest 4.2-compatible version
- [ ] `USE_L10N` and `TEMPLATE_DEBUG` removed from settings (after the Django bump — see order note)
- [ ] `makemigrations` generates no unexpected migrations for local apps
- [ ] Full test suite passes: `make dev_test` in the rebuilt image
- [ ] JSONField behavior unchanged after the jsonfield 3.1.0 → 3.2.0 bump (covered by existing biblioref/oer/leisref tests)
- [ ] No new deprecation warnings that would block Phase 5 (`python -Wd manage.py test`); remaining 4.2→5.x deprecations logged for Phase 5

## Tasks

### 4.1 — Update Python version

**File**: `Dockerfile` line 2
- `FROM python:3.10-alpine AS base` → `FROM python:3.12-alpine AS base`
- Watch pinned deps for setuptools-related install issues at build time (no known blockers)

### 4.2 — Update dependencies

| Package | From | Target | Notes |
|---------|------|--------|-------|
| Django | 3.2.25 | 4.2.x latest patch | Target LTS |
| jsonfield | 3.1.0 | 3.2.0 | Declares Django 4.2–5.2, Python 3.10–3.13; same `dump_kwargs` API |
| django-rosetta | 0.9.9 | newest 4.2-compatible (0.10.x+) | Only other Django-pinned package needing a bump |

Everything else already supports Django 4.2 (see Pre-verified Facts). Opportunistic latest-patch bumps of Django-agnostic packages are fine but not required.

### 4.3 — Settings cleanup (AFTER the Django bump)

**File**: `src/fi-admin/settings.py`
- Remove `USE_L10N = True` (line 77) — **only after** Django is on 4.2: on 3.2 the default is `False`, so removing it early would silently disable localization
- Remove `TEMPLATE_DEBUG = False` (line 400, test block) — dead setting
- `DisableMigrations` — no change needed (already returns `None`)
- `CSRF_TRUSTED_ORIGINS` — not used; nothing to do

### 4.4 — Migrations, tests, deprecation sweep

- Rebuild: `make dev_build`
- `make dev_makemigrations` — expect NO local-app migrations; investigate any that appear
- `make dev_migrate` on the dev database — no errors
- `make dev_test` — all apps green
- `python -Wd manage.py test` — log remaining Django 5.x deprecation warnings to `.ai/logs/` for Phase 5 (expected: `STORAGES`-style hints, form rendering, `logout` via GET if present)

## Implementation Order

1. Task 4.1 + 4.2 (Dockerfile → 3.12, Django → 4.2, jsonfield → 3.2.0, rosetta bump; rebuild)
2. Task 4.3 (settings cleanup, post-bump)
3. Task 4.4 (migrations check, full test run, deprecation sweep)
4. Log in `.ai/logs/`, PR `setup/django-4.2` → `main`

## Risks

- **jsonfield 3.1.0 → 3.2.0**: minor-version bump of the field internals — a behavior change in serialization would surface in the JSONField-heavy app tests (biblioref, oer, leisref); check its CHANGES for anything affecting `dump_kwargs` handling
- **rosetta 0.10.x**: minor API/URL changes possible; Rosetta isn't covered by tests — manual check deferred to validation
- **SQLite-only test coverage**: tests never exercise MySQL; behavior on MySQL 8 is only proven in the validation environment (accepted, same gap as Phase 3)

## Plan Deviations

- Plan task **4.1 (native JSONField migration) dropped** — jsonfield 3.2.0 officially supports Django 4.2–5.2, so the migration is unnecessary for this upgrade path. The plan file's Phase 4/Risk Registry entries about the TEXT→JSON migration no longer apply.
