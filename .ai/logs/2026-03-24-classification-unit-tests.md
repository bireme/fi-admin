# Classification App - Unit Tests

**Date:** 2026-03-24

## Summary

Created unit tests for the `classification` app's `classify` and `get_children_list` views.

## Files Created

- `src/classification/tests.py` — 11 test cases across 2 test classes

## Test Cases

### ClassifyTest (7 tests)
- `test_classify_get` — GET renders template with empty relations and community list
- `test_classify_set_relationship` — POST with `set` creates Relationship objects
- `test_classify_unset_relationship` — POST with `unset` deletes existing Relationships
- `test_classify_set_and_unset` — POST with both set and unset in same request
- `test_classify_set_duplicates` — duplicate IDs in set list create only one Relationship
- `test_classify_unset_nonexistent` — unset for non-existent relationship doesn't error
- `test_classify_get_or_create_existing` — set with existing relationship doesn't create duplicate

### GetChildrenListTest (4 tests)
- `test_get_children_community` — returns community-flagged children with type='community'
- `test_get_children_collection` — returns non-community children with type='collection'
- `test_get_children_empty` — returns empty list when no children exist
- `test_get_children_sorted` — children returned sorted by name

## Results

All 11 tests passing.
