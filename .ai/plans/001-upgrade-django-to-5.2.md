# Django Upgrade Plan: 2.2.24 → 5.2 LTS

## Context

The fi-admin project runs Django 2.2.24 on Python 3.7.8 — both are EOL. The goal is to reach Django 5.2 LTS (latest) through incremental LTS-to-LTS upgrades. The project has 26 Django apps, 20+ models files, 8 Haystack search indexes, Tastypie API resources, and only 52 test methods covering 5 of 26 apps. Several dependencies are abandoned or incompatible with modern Django.

**Upgrade path**: Django 2.2 → 3.2 LTS → 4.2 LTS → 5.2 LTS
**Python path**: 3.7.8 → 3.9.x → 3.10.x → 3.14

---

## Phase 1: Test Foundation (on Django 2.2, Python 3.7)

**Goal**: Build a regression safety net before any Django changes.

### 1.1 — Improve test infrastructure (keep Django unittest, add coverage)
- [ ] Add `coverage` to `requirements-dev.txt`
- [ ] Add `.coveragerc` for coverage configuration
- [ ] Update `bireme/run_tests.sh` to run ALL apps (not just 5)
- [ ] Add Makefile target `dev_coverage` for coverage reports
- Keep existing `BaseTestCase` and `manage.py test` as the test runner

### 1.2 — Replace `model-mommy` with `model-bakery`
- [ ] Replace `model-mommy==2.0.0` → `model-bakery` in `requirements-dev.txt`
- [ ] Update imports in test files: `from model_mommy import mommy` → `from model_bakery import baker`
- [ ] Update calls: `mommy.make(...)` → `baker.make(...)`
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
- [ ] Create/expand `bireme/api/tests.py`
- [ ] Test GET list + GET detail for main Tastypie resources
- [ ] Resources to test: bibliographic, events, multimedia, oer, legislation, title, institution, classification

### 1.5 — Fix `assertEquals` → `assertEqual`
- **Files**: `events/tests.py`, `main/tests.py`, `suggest/tests.py`, `multimedia/tests.py`

### 1.6 — Run baseline coverage report
- [ ] Run full test suite with coverage
- [ ] Document baseline coverage percentage per app

**Verification**: `python manage.py test` passes for all apps, coverage report generated.

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

**Verification**: Full test suite passes, no deprecation warnings with `python -Wd manage.py test`.

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
- [ ] All tests pass
- [ ] `python manage.py check --deploy` — no critical errors
- [ ] `python manage.py migrate` — no errors
- [ ] All Tastypie API endpoints return correct data
- [ ] Form submissions work (biblioref, events, suggest)
- [ ] Admin interface loads
- [ ] Login/authentication works
- [ ] Haystack search indexes rebuild without errors
- [ ] Rosetta translation interface works

---

## Phase 4: Django 3.2 → 4.2 LTS (Python 3.9 → 3.10)

**Goal**: Second major version jump.

### 4.1 — Pre-upgrade: Migrate `jsonfield` to native `JSONField` (keep TEXT storage)
- Django 3.1+ includes `django.db.models.JSONField`
- **File**: `bireme/utils/fields.py` — change `JSONField` to inherit from `django.db.models.JSONField`
- Override `get_internal_type()` to return `"TextField"` — keeps MySQL TEXT columns, zero data migration risk
- Preserve custom `formfield()` and `dumps_for_display()` methods
- Remove `jsonfield==3.1.0` from `requirements.txt`

### 4.2 — Update Python version
- **File**: `Dockerfile` — `FROM python:3.10-alpine`

### 4.3 — Update dependency versions

| Package | From (3.2) | To (4.2) | Notes |
|---------|-----------|----------|-------|
| Django | 3.2.25 | 4.2.x (latest) | Target LTS |
| mysqlclient | 2.1.x | 2.2.x | |
| django-haystack | 3.2.1 | 3.3.0 | |
| django-rosetta | 0.10.0 | 0.10.1 | |
| django-tinymce | 3.5.0 | 3.7.x | |
| django-debug-toolbar | 3.8.x | 4.2.x | |
| elastic-apm | 6.15.x | 6.22.x | |

### 4.4 — Fix Django 4.x breaking changes
- [ ] Remove `USE_L10N` from settings (always True in Django 4.0+)
- [ ] Remove `TEMPLATE_DEBUG` from settings if still present
- [ ] Verify `CSRF_TRUSTED_ORIGINS` has full scheme (`https://...`) if used
- [ ] Review `DisableMigrations` class in test settings for compatibility

### 4.5 — Run migrations and test

**Verification**: Same checklist as Phase 3 + verify JSONField works correctly with TEXT storage backend.

---

## Phase 5: Django 4.2 → 5.2 LTS (stay Python 3.10+)

**Goal**: Final upgrade to target version.

### 5.1 — Update dependency versions

| Package | From (4.2) | To (5.2) | Notes |
|---------|-----------|----------|-------|
| Django | 4.2.x | 5.2.x | Final target LTS |
| django-tastypie | 0.14.7+ | Verify support | **CRITICAL RISK** — may need fork or DRF migration |
| django-haystack | 3.3.0 | 3.3.0+ or newer | Verify 5.2 support |
| django-tinymce | 3.7.x | 4.x | |
| django-debug-toolbar | 4.2.x | 4.4.x | |

### 5.2 — Fix Django 5.x breaking changes
- [ ] Verify form rendering (Django 5.0 uses template-based rendering by default)
- [ ] Check for any `Meta.index_together` → `Meta.indexes` (none found currently)
- [ ] Remove `default_app_config` if not done in Phase 2
- [ ] Review password hashers compatibility

### 5.3 — Handle `django-tastypie` compatibility
- **CRITICAL RISK**: Tastypie may not support Django 5.2
- Evaluate compatibility when we reach this phase and decide on the best approach (fork, patch, or migrate) based on actual situation

### 5.4 — Final migrations and test

**Verification**:
- [ ] Full test suite passes
- [ ] All API endpoints functional (manual + automated)
- [ ] Production-like environment deployment test
- [ ] Performance comparison with baseline
- [ ] `python manage.py check --deploy` clean

---

## Risk Registry

| Risk | Impact | Mitigation |
|------|--------|------------|
| `django-tastypie` incompatible with Django 5.x | **HIGH** | Test early; have fork/DRF migration plan ready |
| `jsonfield` → native JSONField data loss (MySQL TEXT→JSON) | **HIGH** | Test with production data copy; write reversible migration |
| `django-form-utils` replacement breaks biblioref forms | **MEDIUM** | Only 1 file uses it; thorough fieldset testing |
| `django-haystack` incompatible with 5.x | **MEDIUM** | 8 search index files; check compatibility early |
| Test coverage gaps hide regressions | **HIGH** | Phase 1 test expansion is the foundation |
| Third-party package version conflicts | **MEDIUM** | Test each package upgrade individually when possible |

---

## Branch Strategy

| Branch | Content | Merges to |
|--------|---------|-----------|
| `upgrade-django/tests` | Phase 1 — test foundation | `master` (safe, no Django changes) |
| `upgrade-django/deprecations` | Phase 2 — deprecation fixes | `master` (backward-compatible) |
| `upgrade-django/3.2` | Phase 3 — Django 3.2 | `master` |
| `upgrade-django/4.2` | Phase 4 — Django 4.2 | `master` |
| `upgrade-django/5.2` | Phase 5 — Django 5.2 | `master` |

Phases 1 and 2 can be merged to `master` immediately since all changes are backward-compatible with Django 2.2.

---

## Critical Files Reference

| File | Why it matters |
|------|---------------|
| `bireme/utils/fields.py` | Custom JSONField, `from_db_value(context)` signature, `smart_text` import |
| `bireme/biblioref/forms.py` | Only consumer of abandoned `django-form-utils` |
| `bireme/api/ws_decs_serializer.py` | Uses `django.utils.six`, `force_text`, `smart_bytes` |
| `bireme/fi-admin/settings.py` | Needs `DEFAULT_AUTO_FIELD`, bug fix, deprecation removals |
| `requirements.txt` | All dependency versions — updated at each phase |
| `Dockerfile` | Python version — updated at phases 3 and 4 |
| `bireme/utils/tests.py` | `BaseTestCase` — foundation for all test expansion |
