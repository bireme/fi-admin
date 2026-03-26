# Title List View Unit Tests

**Date:** 2026-03-26

## Summary

Added `TitleListViewTest` class to `src/title/tests.py` with 9 tests covering the `TitleListView` and `TitleCatalogView` list view functionality.

## Tests Added

| Test | Description |
|------|-------------|
| `test_list_search_by_title` | `?s=` searches title via icontains |
| `test_list_search_by_short_title` | `?short_title=` searches shortened_title via icontains |
| `test_list_search_by_issn` | `?issn=` filters by exact ISSN |
| `test_list_search_by_secs_number` | `?secs_number=` filters by exact secs_number |
| `test_list_search_by_id_number` | `?id=` filters by id_number |
| `test_list_empty_search_returns_all` | Empty search returns all records |
| `test_list_ordering` | Descending sort with `?order=-&orderby=title` |
| `test_list_context_data` | Context contains `actions` key |
| `test_list_unauthenticated_redirects` | Unauthenticated access returns 302 |

## Files Modified

- `src/title/tests.py` — added `TitleListViewTest` class with helper method `_create_title()`

## Pattern

Follows the same structure as `OERListViewTest` (`src/oer/tests.py`) and `LeisRefListViewTest` (`src/leisref/tests.py`).
