# Django Upgrade Phase 2 — Deprecation Fixes

**Date**: 2026-05-27
**Branch**: `upgrade-django/deprecations` (from `main`)

## Changes Made

### 2.1 — Replaced `ugettext_lazy` / `ugettext` → `gettext_lazy` / `gettext`
- Bulk replacement across 72 Python files in `src/`
- Includes import statements and one direct `translation.ugettext()` call in `api/decs_first_level.py`

### 2.2 — Fixed `django.utils.six` and encoding imports
- `src/api/ws_decs_serializer.py`: Removed `from django.utils import six`, replaced `force_text` → `force_str`, replaced `six.text_type` → `str`
- `src/utils/fields.py`: Removed unused `from django.utils.encoding import smart_text`

### 2.4 — Replaced abandoned `django-form-utils`
- Created `src/utils/betterforms.py` with minimal `BetterModelForm`, `FieldsetCollection`, and `Fieldset` classes
- Updated `src/biblioref/forms.py` import to use new shim
- Removed `django-form-utils==1.0.3` from `requirements.txt`
- Removed `'form_utils'` from `INSTALLED_APPS` in `src/fi-admin/settings.py`

### 2.5 — Removed dead `recaptcha-client` dependency
- Removed `recaptcha-client==1.0.6` from `requirements.txt` (was never imported)

### 2.6 — Removed `default_app_config`
- Removed `default_app_config = 'utils.apps.UtilsAppConfig'` from `src/utils/__init__.py`

## Deferred
- Task 2.3 (`from_db_value` context parameter in `utils/fields.py`) — deferred to Phase 3 (Django 3.2 upgrade)

## Test Results
- All 192 tests pass across 13 apps (0 failures, 5 skipped)

All 200 tests pass across 13 apps (0 failures, 5 skipped). That's 8 new tests added:

**New tests:**

| Test                                                                  | What it validates                                |
| --------------------------------------------------------------------- | ------------------------------------------------ |
| `FieldsetTest.test_fieldset_yields_bound_fields_for_defined_fields`   | Fieldset iterates correct bound fields           |
| `FieldsetTest.test_fieldset_skips_fields_not_in_form`                 | Fieldset handles missing fields gracefully       |
| `FieldsetTest.test_fieldset_adds_row_attrs`                           | Template-required `row_attrs` attribute is set   |
| `FieldsetTest.test_fieldset_attributes`                               | name/legend/classes/description pass through     |
| `FieldsetTest.test_fieldset_classes_as_string`                        | Classes work as string (not just list)           |
| `FieldsetCollectionTest.test_iteration_yields_fieldsets`              | Collection yields named Fieldset objects         |
| `FieldsetCollectionTest.test_empty_fieldsets`                         | None fieldsets returns empty iteration           |
| `FieldsetCollectionTest.test_fieldset_collection_fields_are_iterable` | End-to-end: collection → fieldset → bound fields |
| `WsDecsSerializerTest.test_to_etree_string_value`                     | String data uses `isinstance(str)` path          |
| `WsDecsSerializerTest.test_to_etree_integer_value`                    | Non-string data uses `force_str()` path          |
| `WsDecsSerializerTest.test_to_etree_none_value`                       | Null values produce no text                      |
| `WsDecsSerializerTest.test_to_etree_unicode_value`                    | Unicode strings handled correctly                |
| `WsDecsSerializerTest.test_to_etree_dict`                             | Dict → XML element with children                 |
| `WsDecsSerializerTest.test_to_etree_list`                             | List → multiple child elements                   |
| `WsDecsSerializerTest.test_to_etree_dict_with_attr_key`               | `attr` dict becomes XML attributes               |
| `WsDecsSerializerTest.test_to_etree_boolean_value`                    | Boolean converted via `force_str()`              |

Total test count went from 192 → 200. All passing.
