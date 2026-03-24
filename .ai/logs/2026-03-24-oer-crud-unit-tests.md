# OER CRUD Unit Tests

**Date:** 2026-03-24

## Summary

Implemented comprehensive CRUD unit tests for the OER (Open Educational Resource) app at `src/oer/tests.py`, following the same pattern used in `src/leisref/tests.py` and `src/multimedia/tests.py`.

## Changes

### `src/oer/tests.py`
- Added `minimal_form_data()` helper with all required formset management data
- Added `complete_form_data()` helper with publication-required fields (learning_objectives, description, creator, type, language, license, learning_context, descriptor, thematic area)
- Added `create_oer_object()` helper that creates two OER records from different cooperative centers
- Added `OERTest` class with 4 CRUD tests:
  - `test_list_oer` — verifies list filtering by user
  - `test_add_oer` — verifies OER creation and cooperative center assignment
  - `test_edit_oer` — verifies edit form rendering and submission
  - `test_delete_oer` — verifies deletion of OER and cascaded related objects
- Added `OERSearchTest` class with `test_search_id` — verifies search by ID filtering

## Test Results

All 5 tests pass: `make dev_test_app app=oer`
