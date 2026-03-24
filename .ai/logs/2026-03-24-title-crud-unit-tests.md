# Title CRUD Unit Tests

**Date:** 2026-03-24

## Summary

Implemented comprehensive CRUD unit tests for the Title (serial titles/journals) app at `src/title/tests.py`, following the same pattern used in `src/oer/tests.py` and `src/leisref/tests.py`.

## Changes

### `src/title/tests.py` (new file)
- Added `minimal_form_data()` helper with all 10 formset management data, required descriptor entry, `action='save'` field, and `state` field (required when country is BR)
- Added `create_title_object()` helper that creates two Title records from different cooperative centers with M2M country and related Descriptor
- Added `TitleTest` class with 4 CRUD tests:
  - `test_list_title` — verifies all titles visible (no owner filtering in title app)
  - `test_add_title` — verifies Title creation and cooperative center assignment
  - `test_edit_title` — verifies edit form rendering and submission
  - `test_delete_title` — verifies deletion of Title and cascaded Descriptor/Keyword objects
- Added `TitleSearchTest` class with `test_search_id` — verifies search by id_number filtering

## Notes

- Title app has 10 formsets (most of any app) and requires at least 1 descriptor via `DescriptorRequired`
- `TitleForm.save()` has a pre-existing bug: `Title.objects.latest('id')` raises DoesNotExist on empty table. Worked around by creating a seed Title in setUp.
- Title's status is CharField ('C'/'D'/'?'), not integer, so `is_valid_for_publication` never triggers.
- Form requires `action='save'` in POST data for successful save+redirect.
- When country is 'BR', `state` field is mandatory (clean_state validation).

## Test Results

All 5 tests pass: `make dev_test_app app=title`
