# Institution CRUD Unit Tests

**Date:** 2026-03-24

## Summary

Implemented CRUD unit tests for the `institution` app following the pattern established in `src/oer/tests.py`.

## Changes

### Modified: `src/institution/tests.py`

- **`login_admin_institution()`** — Helper that wraps `login_admin()` and patches the user profile to add `user_type: "advanced"`, which is required by the institution views' `dispatch()` method (checks both `DirIns` role and `user_type == 'advanced'`).

- **`minimal_form_data(country_id)`** — Returns minimum fields for Institution form submission, including management forms for 4 inline formsets: `contact_set`, `url_set`, `unitlevel_set`, `adm_set`.

- **`create_institution_object(user, country)`** — Creates two Institution objects (BR1.1 and PY3.1) with related Contact and URL records for testing.

- **`InstitutionTest`** (4 tests):
  - `test_list_institution` — Verifies list filtering by `cc_code=user_cc`
  - `test_add_institution` — Tests POST to create new institution
  - `test_edit_institution` — Tests GET form display and POST update
  - `test_delete_institution` — Tests delete confirmation and cascade (Contact, URL, Adm)

- **`InstitutionSearchTest`** (1 test):
  - `test_search_cc_code` — Tests CC code pattern search (`cc_code__istartswith`)

## Key Decisions

- Used CC code search (not name search) for the search test, because name search uses `FULLTEXT_SEARCH` which triggers MySQL-specific `__search` lookups that fail in the test database.
- Delete confirmation test checks for `cc_code` in response instead of translated text, since the template uses `{% trans %}` tags.

## Verification

All 5 tests pass: `make dev_test_app app=institution`
