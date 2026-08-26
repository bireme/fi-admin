# Phase 2: Deprecation Fixes (on Django 2.2, Python 3.7)

## Goal

Fix all known deprecations and remove abandoned dependencies while still on Django 2.2. All changes are backward-compatible — nothing breaks on the current stack.

## Branch

`upgrade-django/deprecations` — branched from `main`

## Acceptance Criteria

- [ ] All `ugettext_lazy` / `ugettext` replaced with `gettext_lazy` / `gettext` across 72 files
- [ ] `django.utils.six` and `force_text` removed from `api/ws_decs_serializer.py`
- [ ] Unused `smart_text` import removed from `utils/fields.py`
- [ ] `django-form-utils` replaced with minimal shim in `utils/betterforms.py`
- [ ] `recaptcha-client` removed from `requirements.txt` (dead dependency)
- [ ] `default_app_config` removed from `utils/__init__.py`
- [ ] `form_utils` removed from `INSTALLED_APPS` in settings
- [ ] `django-form-utils==1.0.3` removed from `requirements.txt`
- [ ] Full test suite passes (`make dev_test`)
- [ ] No new deprecation warnings introduced

## Tasks

### 2.1 — Replace `ugettext_lazy` / `ugettext` with `gettext_lazy` / `gettext`

**Approach**: Single bulk operation (sed) across all 72 files.

**Import patterns to replace**:
- `from django.utils.translation import ugettext_lazy as _` → `from django.utils.translation import gettext_lazy as _`
- `from django.utils.translation import ugettext as __` → `from django.utils.translation import gettext as __`
- `from django.utils.translation import ugettext_lazy as _, get_language` → same with `gettext_lazy`
- `from django.utils.translation import ugettext_lazy as _, get_language, activate` → same with `gettext_lazy`
- `from django.utils.translation import ugettext as _, get_language` → same with `gettext`

**Direct call** (1 file):
- `api/decs_first_level.py` line 9: `translation.ugettext(category)` → `translation.gettext(category)`

### 2.2 — Fix `django.utils.six` and encoding imports

**File: `api/ws_decs_serializer.py`**:
- Remove `from django.utils import six`
- Replace `from django.utils.encoding import force_text, smart_bytes` → `from django.utils.encoding import force_str, smart_bytes`
- Replace `isinstance(simple_data, six.text_type)` → `isinstance(simple_data, str)` (keep if/else structure)
- Replace `force_text(simple_data)` → `force_str(simple_data)`

**File: `utils/fields.py`**:
- Remove unused `from django.utils.encoding import smart_text` (line 5)

### 2.3 — Fix `from_db_value` signature

**DEFERRED TO PHASE 3** — user prefers not to change the signature until Django is actually updated to 3.2 where it's required. The `context` parameter is deprecated but still accepted in 2.2.

### 2.4 — Replace abandoned `django-form-utils`

**Strategy**: Create `utils/betterforms.py` with minimal shim.

**What to implement**:
- `BetterModelForm(ModelForm)` — subclass of `ModelForm` that adds `_fieldset_collection` attribute (initialized to `None`)
- `FieldsetCollection` — wraps form fields into named fieldsets for template rendering

**Consumer**: `biblioref/forms.py` (only file)
- Change import: `from form_utils.forms import BetterModelForm, FieldsetCollection` → `from utils.betterforms import BetterModelForm, FieldsetCollection`
- The `BiblioRefForm` uses:
  - Inherits from `BetterModelForm`
  - `self._fieldsets` (set from kwargs in `__init__`)
  - `self._fieldset_collection` (initialized by `BetterModelForm.__init__`)
  - `FieldsetCollection(self, self._fieldsets)` in `fieldsets()` method
  - `self._fieldsets` iterated in `is_visiblefield()` for field visibility checks

**Cleanup**:
- Remove `django-form-utils==1.0.3` from `requirements.txt`
- Remove `'form_utils'` from `INSTALLED_APPS` in `fi-admin/settings.py`

### 2.5 — Remove dead `recaptcha-client` dependency

**Action**: Remove `recaptcha-client==1.0.6` from `requirements.txt`.

The package is never imported. `suggest/views.py` already has a custom `validate_recaptcha()` using `urllib` to call Google's reCAPTCHA API directly.

### 2.6 — Remove `default_app_config`

**File**: `utils/__init__.py` line 4
**Action**: Remove `default_app_config = 'utils.apps.UtilsAppConfig'`

Deprecated in Django 3.2, but removing it is safe on 2.2 since Django auto-discovers `AppConfig` subclasses from `apps.py`.

## Implementation Order

1. Create branch `upgrade-django/deprecations` from `main`
2. Task 2.1 — bulk ugettext replacement (biggest change, do first)
3. Task 2.2 — six and encoding fixes
4. Task 2.4 — form-utils replacement (most complex, needs testing)
5. Task 2.5 — remove recaptcha-client
6. Task 2.6 — remove default_app_config
7. Run full test suite
8. Create PR to master

## Notes

- Task 2.3 (`from_db_value` context parameter) is intentionally deferred to Phase 3
- All changes are backward-compatible with Django 2.2 — safe to merge to main immediately
- The `BetterModelForm` shim needs to be tested with the biblioref form rendering to ensure fieldsets display correctly
