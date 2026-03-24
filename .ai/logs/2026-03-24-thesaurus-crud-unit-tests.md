# Thesaurus CRUD Unit Tests

**Date:** 2026-03-24

## Summary

Implemented CRUD unit tests for the thesaurus app covering Descriptors, Qualifiers, and search functionality.

## Changes

### Created: `src/thesaurus/tests.py`

- **Helper functions:**
  - `create_thesaurus()` — Creates a Thesaurus object with required fields
  - `minimal_form_data_descriptor(thesaurus_id)` — Minimum form data for Descriptor Step 1 (6 inline formsets)
  - `minimal_form_data_qualifier(thesaurus_id)` — Minimum form data for Qualifier Step 1 (2 inline formsets)
  - `create_descriptor_with_term(thesaurus, user)` — Creates full chain: IdentifierDesc → IdentifierConceptListDesc → TermListDesc
  - `create_qualifier_with_term(thesaurus, user)` — Creates full chain: IdentifierQualif → IdentifierConceptListQualif → TermListQualif

- **DescriptorTest (4 tests):**
  - `test_list_descriptor` — Lists terms via DescListView with `choiced_thesaurus` and `visited` params
  - `test_add_descriptor` — Creates descriptor Step 1, verifies auto-generated `decs_code` and `descriptor_ui`
  - `test_edit_descriptor` — Posts edit form with description and tree_number formsets (GET skipped due to template bug)
  - `test_delete_descriptor` — Confirms and deletes bare IdentifierDesc (no PROTECT-related objects)

- **QualifierTest (4 tests):**
  - `test_list_qualifier`, `test_add_qualifier`, `test_edit_qualifier`, `test_delete_qualifier`

- **DescriptorSearchTest (1 test):**
  - `test_search_term` — Searches terms by string, verifies filtering

## Key differences from OER/Title tests

1. Multi-step creation flow (Step 1 → redirect to Step 2 for concept+term)
2. List view queries TermListDesc/TermListQualif, not the main identifier model
3. Inline formset prefixes based on `related_name` (e.g., `descriptiondesc`, `dtreenumbers`, `pharmacodesc`)
4. Tree number validation required (odd length, letter start, digit at position 3)
5. Auto-generated `decs_code` and `descriptor_ui`/`qualifier_ui` via `code_controller`
6. Delete uses PROTECT on all FKs — tests use bare identifiers without related objects

## Known issue discovered

`descriptor_edit_register.html` line 579 has a `SuspiciousFileOperation` bug: uses `{% static '/js/jquery.formset.js' %}` (leading `/`) instead of `{% static 'js/jquery.formset.js' %}`. This causes 400 on GET in tests.

## Verification

```bash
make dev_test_app app=thesaurus
# Ran 9 tests in ~5s — all OK
```
