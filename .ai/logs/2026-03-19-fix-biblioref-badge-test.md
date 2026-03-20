# Fix: biblioref badge test — exclude deleted sources from reference list

## Date: 2026-03-19

## Problem
`test_exclude_deleted_sources_from_results` failed because the view returned deleted source records in the queryset, making the badge count 2 instead of the expected 1.

## Root cause
`BiblioRefGenericListView.get_queryset()` in `bireme/biblioref/views.py` had no logic to exclude deleted sources (status=3, treatment_level='') from the main reference list. Deleted analytics (treatment_level='as') should remain visible.

## Fix
Added exclusion at the end of `get_queryset()` (line ~244):

```python
# exclude deleted sources from results
object_list = object_list.exclude(status=3, treatment_level='')
```

This follows the same pattern already used for draft sources at line 239.

## Files modified
- `bireme/biblioref/views.py` — added `.exclude(status=3, treatment_level='')` before return in `get_queryset()`

## Verification
`make dev_test_app app=biblioref` — all 9 tests pass (OK, 5 intentionally skipped).
