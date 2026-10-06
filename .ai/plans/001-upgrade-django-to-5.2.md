# Django Upgrade Plan: 2.2.24 → 5.2 LTS

## Context

The fi-admin project runs Django 2.2.24 on Python 3.7.8 — both are EOL. The goal is to reach Django 5.2 LTS (latest) through incremental LTS-to-LTS upgrades. The project has 26 Django apps, 20+ models files, 8 Haystack search indexes, Tastypie API resources, and only 52 test methods covering 5 of 26 apps. Several dependencies are abandoned or incompatible with modern Django.

**Upgrade path**: Django 2.2 → 3.2 LTS → 4.2 LTS → 5.2 LTS
**Python path**: 3.7.8 → 3.9.x → 3.10.x → 3.14

---

## Phase 1: Test Foundation (on Django 2.2, Python 3.7)

**Goal**: Build a regression safety net before any Django changes.

### 1.1 — Improve test infrastructure (keep Django unittest, add coverage)
- [x] Add `coverage` to `requirements-dev.txt`
- [x] Add `.coveragerc` for coverage configuration
- [x] Update `bireme/run_tests.sh` to run ALL apps (not just 5)
- [x] Add Makefile target `dev_coverage` for coverage reports
- Keep existing `BaseTestCase` and `manage.py test` as the test runner

### 1.2 — Replace `model-mommy` with `model-bakery`
- [x] Replace `model-mommy==2.0.0` → `model-bakery` in `requirements-dev.txt`
- [x] Update imports in test files: `from model_mommy import mommy` → `from model_bakery import baker`
- [x] Update calls: `mommy.make(...)` → `baker.make(...)`
- **Files**: `biblioref/tests.py`, `leisref/tests.py`, `multimedia/tests.py`, `main/tests.py`

### 1.3 — Write smoke tests for untested apps
Priority order (by complexity and risk):

| App | What to test |
|-----|-------------|
| `institution` | Model CRUD, list/create/edit views with role access |
| `leisref` | Model CRUD, views, legislation-specific forms |
| `oer` | Model CRUD, views (13 models, complex) |
| `thesaurus` | Model creation across 3 model files (18 models) |
| `title` | Model CRUD, views (11 models) |
| `classification` | Model CRUD (3 models, simpler) |
| `attachments` | Upload/delete flow |
| `help` | Page rendering |
| `database` | Model CRUD |
| `text_block` | Model CRUD |
| `related` | LinkedResearchData, LinkedResource models |
| `biremelogin` | Authentication flow, EmailModelBackend |

Each app test should cover at minimum:
- Model creation with required fields
- List view returns 200 for authenticated user
- Create view renders form
- Unauthenticated access returns redirect/403

### 1.4 — Write API endpoint tests
- [x] Create/expand `bireme/api/tests.py`
- [x] Test GET list + GET detail for main Tastypie resources
- [x] Resources to test: bibliographic, events, multimedia, oer, legislation, title, institution, classification

### 1.5 — Fix `assertEquals` → `assertEqual`
- [x] **Files**: `events/tests.py`, `main/tests.py`, `suggest/tests.py`, `multimedia/tests.py`, `title/tests.py`, `oer/tests.py`, `leisref/tests.py`

### 1.6 — Run baseline coverage report
- [x] Run full test suite with coverage
- [x] Document baseline coverage percentage per app (see `.ai/logs/2026-04-08-baseline-coverage-report.md`) — **55% overall**

**Verification**: `make dev_test` passes for all apps, coverage report generated.

---

## Phase 2: Deprecation Fixes (on Django 2.2, Python 3.7)

**Goal**: Fix all known deprecations while still on Django 2.2 — all changes are backward-compatible.

### 2.1 — Replace `ugettext_lazy` / `ugettext` with `gettext_lazy` / `gettext`
- Mechanical find-and-replace across **77 files**
- `from django.utils.translation import ugettext_lazy as _` → `from django.utils.translation import gettext_lazy as _`
- `from django.utils.translation import ugettext as __` → `from django.utils.translation import gettext as __`
- Both aliases exist in Django 2.2, so this is safe

### 2.2 — Fix `django.utils.six` and encoding imports
- **File**: `bireme/api/ws_decs_serializer.py`
  - Remove `from django.utils import six` — replace `six.text_type` with `str`
  - Replace `from django.utils.encoding import force_text, smart_bytes` → `from django.utils.encoding import force_str, smart_bytes`
  - Replace `force_text(...)` calls → `force_str(...)`
- **File**: `bireme/utils/fields.py`
  - Remove `from django.utils.encoding import smart_text` (unused import — `smart_text` is imported but never called in the file)

### 2.3 — Fix `from_db_value` signature (CRITICAL for Django 3.0)
- **File**: `bireme/utils/fields.py` line 79
- Change: `def from_db_value(self, value, expression, connection, context):`
- To: `def from_db_value(self, value, expression, connection):`
- The `context` parameter was removed in Django 3.0. This change is backward-compatible with 2.2.

### 2.4 — Replace abandoned `django-form-utils`
- **File**: `bireme/biblioref/forms.py` (only consumer)
- Uses `BetterModelForm` and `FieldsetCollection` for form fieldset support
- **Strategy**: Create `bireme/utils/betterforms.py` with minimal reimplementation of:
  - `BetterModelForm(ModelForm)` — adds `_fieldsets` / `_fieldset_collection` support
  - `FieldsetCollection` — groups form fields into named fieldsets
- Remove `django-form-utils==1.0.3` from `requirements.txt`

### 2.5 — Replace `recaptcha-client`
- `recaptcha-client==1.0.6` is very old
- Check usage in `suggest/` app and replace with `django-recaptcha` or inline verification

### 2.6 — Remove `default_app_config`
- **File**: `bireme/utils/__init__.py` line 4
- Remove: `default_app_config = 'utils.apps.UtilsAppConfig'`
- Deprecated in Django 3.2, removed in 5.0. Safe to remove now.

**Verification**: Full test suite passes, no deprecation warnings with `make dev_test`.

---

## Phase 3: Django 2.2 → 3.2 LTS (Python 3.7 → 3.9)

**Goal**: First major version jump.

### 3.1 — Update Python version
- **File**: `Dockerfile` line 2
- Change: `FROM python:3.7.8-alpine` → `FROM python:3.9-alpine`

### 3.2 — Update dependency versions

| Package | From | To | Notes |
|---------|------|----|-------|
| Django | 2.2.24 | 3.2.25 | Target LTS |
| mysqlclient | 1.4.6 | 2.1.x | Python 3.9 compat |
| django-tastypie | 0.14.3 | 0.14.7+ | Verify 3.2 support |
| django-haystack | 2.8.1 | 3.2.1 | Major version bump |
| django-rosetta | 0.9.4 | 0.10.0 | |
| django-tinymce | 3.0.2 | 3.5.0 | |
| django-multiselectfield | 0.1.12 | 0.1.13 | |
| django-crum | 0.7.8 | 0.7.9 | |
| elastic-apm | 6.2.2 | 6.15.x | |
| django-debug-toolbar | 2.2 | 3.8.x | |
| gunicorn | 20.1.0 | 21.2.0 | |
| requests | 2.24.0 | 2.31.x | |
| lxml | 4.6.3 | 4.9.x | |

### 3.3 — Add `DEFAULT_AUTO_FIELD` to settings
- **File**: `bireme/fi-admin/settings.py`
- Add: `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'`
- This preserves existing integer PKs and prevents auto-migration to BigAutoField

### 3.4 — Fix settings bug
- **File**: `bireme/fi-admin/settings.py` line ~294
- `int(os.environ.get("EXPOSE_API_ONLY"), 0)` → `int(os.environ.get("EXPOSE_API_ONLY", 0))`
- (The `, 0` is currently parsed as base argument to `int()`, not default for `get()`)

### 3.5 — Run migrations
- `python manage.py makemigrations` — check for auto-generated migrations
- `python manage.py migrate`

### 3.6 — Fix any new deprecation warnings
- Run `python -Wd manage.py test` and fix warnings

**Verification**:
- [x] All tests pass
- [x] `make dev_test` — no critical errors
- [x] `python manage.py migrate` — no errors
- [x] All Tastypie API endpoints return correct data
- [x] Form submissions work (biblioref, events, suggest)
- [x] Admin interface loads
- [x] Login/authentication works
- [x] Haystack search indexes rebuild without errors
- [x] Rosetta translation interface works

---

## Phase 4: Django 3.2 → 4.2 LTS (Python 3.10 → 3.12)

**Goal**: Second major version jump.

### 4.1 — Keep `jsonfield`, bump to 3.2.0 (decision 2026-08-26, supersedes native-JSONField migration)
- Original plan (migrate to `django.db.models.JSONField`) dropped: `jsonfield==3.2.0` officially declares Django 4.2–5.2 and Python 3.10–3.13 support
- `utils.fields.JSONField` and all `dump_kwargs` usage stay unchanged
- `requirements.txt`: `jsonfield==3.1.0` → `jsonfield==3.2.0`

### 4.2 — Update Python version
- **File**: `Dockerfile` — `FROM python:3.12-alpine`

### 4.3 — Update dependency versions

| Package | From (3.2) | To (4.2) | Notes |
|---------|-----------|----------|-------|
| Django | 3.2.25 | 4.2.x (latest) | Target LTS |
| django-rosetta | 0.10.0 | 0.10.1 | |


### 4.4 — Fix Django 4.x breaking changes
- [x] Remove `USE_L10N` from settings (always True in Django 4.0+)
- [x] Remove `TEMPLATE_DEBUG` from settings if still present
- [x] Verify `CSRF_TRUSTED_ORIGINS` has full scheme (`https://...`) if used
- [x] Review `DisableMigrations` class in test settings for compatibility

### 4.5 — Run migrations and test

**Verification**: Same checklist as Phase 3 + verify JSONField works correctly with TEXT storage backend.

---

## Phase 5: Django 4.2 → 5.2 LTS (Python 3.12 → 3.14)

**Goal**: Final upgrade to target version.

### 5.0 — Pre-flight checks (before touching code)
- [x] Check DB server versions for `default` and `decs_portal`: MySQL ≥ 8.0.11 or MariaDB ≥ 10.5 (Django 5.2 minimum)
- [x] Look for legacy password hashes that Django 5.1 can no longer verify (SHA1, UnsaltedSHA1 and UnsaltedMD5 hashers were removed):
      `SELECT COUNT(*) FROM auth_user WHERE password LIKE 'sha1$%' OR password LIKE 'md5$$%' OR password REGEXP '^[0-9a-f]{32}$';`
      If any are found, wrap them with `MD5PasswordHasher` using a data migration, or accept that those users must reset their passwords
- [x] Run `python -Wd manage.py test` on 4.2 and fix any `RemovedInDjango50Warning` / `RemovedInDjango51Warning` (done 2026-09-28, spec `006`; `make dev_test_deprecations`). One warning remains and is expected: `tastypie/compat.py` imports `django.utils.datetime_safe` only when `django.VERSION < (5, 0)`, so it disappears on 5.x

### 5.1 — Keep `jsonfield` (decision 2026-09-28; continues task 4.1)
- `jsonfield==3.2.0` officially supports Django 4.2–5.2, so there is **no migration to native `models.JSONField`**
- `src/utils/fields.py` (`JSONField` subclass, `formfield()`/`dump_kwargs`, `dumps_for_display()`) stays unchanged
- Storage stays TEXT: no schema or data migration needed
- [x] `makemigrations --check --dry-run` shows no changes to JSONField columns (done 2026-10-06, `make dev_makemigrations_check`: "No changes detected")
- [x] Add/confirm tests that save and reload a model with a JSONField (list, dict, `None`, `''` values) and render its form (hidden widget, `indent=None`) (done 2026-10-06, `utils.tests.JSONFieldTest`, plan `019`; `utils` added to `run_tests.sh`/`run_coverage.sh`)
- [x] Run those tests under Python 3.14. jsonfield declares support only up to 3.13; if the tests fail, target `python:3.13-alpine` instead (Django 5.2 supports 3.10–3.14) (done 2026-10-06: `make dev_test_py` → Python 3.14.8 + Django 5.2.18, all 22 `utils` tests pass; the image incl. mysqlclient/lxml builds on 3.14 → **keep 3.14 as the target**)
- [x] Watch PyPI for a jsonfield release declaring Python 3.14 and bump to it when available (checked 2026-10-06: 3.2.0 of 2025-07-04 is still the latest; the project is marked "Inactive")
- **Note — `dump_kwargs` coupling**: jsonfield's `formfield()` hands the model field's own `dump_kwargs` dict to the form field, and `utils.fields.JSONField.formfield()` sets `indent=None` on it. That mutation is why every migration records `dump_kwargs={'ensure_ascii': False, 'indent': None}`; `makemigrations` stays clean only because ModelForms are built (URL checks) before the autodetector runs. `JSONFieldTest.test_formfield_deconstruct_matches_migrations` guards it

### 5.2 — Update Python version
- **File**: `Dockerfile` — change the default of `ARG PYTHON_VERSION=3.12` (added in 5.1) to `3.14`. 3.14 confirmed in 5.1 with `make dev_test_py` (utils tests on Django 5.2.18); the 3.13 fallback is not needed

### 5.3 — Update dependency versions

| Package | From (4.2) | To (5.2) | Notes |
|---------|-----------|----------|-------|
| Django | 4.2.30 | 5.2.x (≥ 5.2.8) | 5.2.8+ required for Python 3.14 |
| jsonfield | 3.2.0 | 3.2.0 (keep) | Supports Django 4.2–5.2 |
| django-tastypie | ~~0.14.7~~ 0.15.1 | 0.15.1 | **Done early in 5.0** (declares Django 4.2–5.2; api tests pass on 4.2) |
| django-haystack | 3.3.0 | 3.4.0 / latest | Check 5.2 support; rebuild indexes |
| django-rosetta | 0.10.3 | latest 0.10.x | |
| django-tinymce | 4.1.0 | 5.0.0 | |
| django-multiselectfield | 1.0.1 | latest | |
| django-debug-toolbar (dev) | ~~4.3.0~~ 5.2.0 | 5.2.0 | **Done early in 5.0**; disabled when running tests |
| model-bakery (dev) | 1.17.0 | latest 1.x | |
| mysqlclient | 2.2.8 | latest 2.2.x | Needs a Python 3.14 wheel/build |
| lxml | 6.1.1 | keep / latest | Needs a Python 3.14 wheel |

Bump one package at a time and run `make dev_test` after each.

### 5.4 — Fix Django 5.x breaking changes
- [x] **Logout via GET removed (5.0)** (done early in 5.0, `menu.html` POST form + `main.tests.LogoutTest`): `src/biremelogin/urls.py` uses `LogoutView`. Replace every `<a href="{% url 'auth_logout' %}">` in templates with a POST `<form>` that includes `{% csrf_token %}`, styled as a link
- [ ] **Password hashers (5.1)**: keep `MD5PasswordHasher` (still present in 5.2); act on the 5.0 pre-flight result. Plan a later switch to `PBKDF2PasswordHasher` with MD5 kept as a fallback
- [ ] **Forms (5.0)**: div-based default form rendering. Check templates that use `{{ form }}` / `{{ form.as_table }}` and the `BetterModelForm` fieldsets used by the biblioref forms
- [ ] **`Model.save()` positional args (5.1 deprecation)**: switch any `save(True, …)` calls to keyword args
- [ ] Remove `index_together` if present (including in old migrations; squash or edit to `indexes`)
- [ ] Check removed APIs: `assertQuerysetEqual` → `assertQuerySetEqual`, `length_is` filter, `django.utils.timezone.utc`, `pytz`, `get_storage_class`, old `assertFormError` signature
- [ ] Settings: confirm `USE_L10N` / `DEFAULT_FILE_STORAGE` / `STATICFILES_STORAGE` are not set (use `STORAGES` if needed)
- [ ] `DisableMigrations` in test settings still works

### 5.5 — Handle `django-tastypie` compatibility
- 0.15.1 installed in 5.0 and the API tests pass on Django 4.2. Still to do after the 5.2 bump: the API test suite (`src/api/tests.py`) plus a manual GET on every resource
- If it breaks, the order of preference is: (1) a small local patch or monkeypatch in `api/`, (2) pin a fork, (3) a DRF migration as its own project (out of scope for this phase)

### 5.6 — Migrations and test
- [ ] `makemigrations --check`: expect no-op migrations only (commit them like Phase 4 did)
- [ ] `make dev_test` with coverage; compare with the 55% baseline
- [ ] `python manage.py rebuild_index` (Haystack) runs without errors

**Verification**:
- [ ] Full test suite passes on Python 3.14 (or the 3.13 fallback)
- [ ] JSONField values round-trip unchanged against a copy of production data (spot-check biblioref/leisref/oer records)
- [ ] Login and **logout (POST)** work; legacy users can still log in
- [ ] All Tastypie API endpoints functional (manual + automated)
- [ ] Admin, Rosetta and TinyMCE load; DeCS popup still works
- [ ] Production-like environment deployment test (`make prod_migrate`)
- [ ] Performance comparison with baseline
- [ ] `python manage.py check --deploy` clean

---

## Risk Registry

| Risk | Impact | Mitigation |
|------|--------|------------|
| `django-tastypie` incompatible with Django 5.x | **HIGH** | Test early; have fork/DRF migration plan ready |
| ~~`jsonfield` → native JSONField data loss~~ (obsolete — jsonfield kept, see task 4.1) | ~~HIGH~~ | jsonfield 3.2.0 supports Django 4.2–5.2; no migration needed |
| `django-form-utils` replacement breaks biblioref forms | **MEDIUM** | Only 1 file uses it; thorough fieldset testing |
| `django-haystack` incompatible with 5.x | **MEDIUM** | 8 search index files; check compatibility early |
| `jsonfield` on Python 3.14 (declared up to 3.13) | ~~MEDIUM~~ LOW | Round-trip tests pass on 3.14 + Django 5.2 (task 5.1, 2026-10-06); fallback `python:3.13-alpine` kept in reserve |
| DB server below MySQL 8.0.11 / MariaDB 10.5 | **HIGH** | Check `default` and `decs_portal` versions before starting Phase 5 (task 5.0) |
| Test coverage gaps hide regressions | **HIGH** | Phase 1 test expansion is the foundation |
| Third-party package version conflicts | **MEDIUM** | Test each package upgrade individually when possible |

---

## Branch Strategy

| Branch | Content | Merges to |
|--------|---------|-----------|
| `setup/test-foundation` | Phase 1 — test foundation | `main` (safe, no Django changes) |
| `setup/deprecation-fixes` | Phase 2 — deprecation fixes | `main` (backward-compatible) |
| `setup/django-3.2` | Phase 3 — Django 3.2 | `main` |
| `setup/django-4.2` | Phase 4 — Django 4.2 | `main` |
| `setup/django-5.2` | Phase 5 — Django 5.2 | `main` |

Phases 1 and 2 can be merged to `main` immediately since all changes are backward-compatible with Django 2.2.

---

## Critical Files Reference

| File | Why it matters |
|------|---------------|
| `src/utils/fields.py` | Custom JSONField (subclass of `jsonfield.JSONField`, kept through 5.2) |
| `src/biremelogin/urls.py` | `LogoutView` via GET removed in Django 5.0 |
| `bireme/biblioref/forms.py` | Only consumer of abandoned `django-form-utils` |
| `bireme/api/ws_decs_serializer.py` | Uses `django.utils.six`, `force_text`, `smart_bytes` |
| `bireme/fi-admin/settings.py` | Needs `DEFAULT_AUTO_FIELD`, bug fix, deprecation removals |
| `requirements.txt` | All dependency versions — updated at each phase |
| `Dockerfile` | Python version — updated at phases 3 and 4 |
| `bireme/utils/tests.py` | `BaseTestCase` — foundation for all test expansion |
