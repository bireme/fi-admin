# Plan: Add List View Tests for Title App

## Context
The title app currently has minimal list view test coverage — just `TitleTest.test_list_title()` and `TitleSearchTest.test_search_id()`. The OER and LeisRef apps recently got comprehensive list view tests (commits `22ccc39`, `4676720`). This plan follows the same pattern to increase title test coverage.

## File to Modify
- `src/title/tests.py` — add a new `TitleListViewTest` class

## Approach
Add a `TitleListViewTest` class following the OER pattern (`src/oer/tests.py:195-378`), adapted for Title-specific filters defined in `TitleCatalogView.get_queryset()` (`src/title/views.py:57-89`).

### Tests to Add

**1. Search functionality** (maps to `get_queryset` filters):
- `test_list_search_by_title` — `?s=` searches `title__icontains`
- `test_list_search_by_short_title` — `?short_title=` searches `shortened_title__icontains`
- `test_list_search_by_issn` — `?issn=` exact match filter
- `test_list_search_by_secs_number` — `?secs_number=` exact match filter
- `test_list_search_by_id` — `?id=` filters by `id_number` (complements existing `TitleSearchTest`)
- `test_list_empty_search_returns_all` — empty `?s=` returns all

**2. Ordering**:
- `test_list_ordering` — `?order=-&orderby=title` applies descending sort

**3. Context data**:
- `test_list_context_data` — response context contains `actions` key

**4. Access control**:
- `test_list_unauthenticated_redirects` — unauthenticated GET returns 302

### Helper
- `_create_title(self, user, title, ..., **overrides)` — creates Title with sensible defaults, similar to OER's `_create_oer`

### Setup
- `setUp`: create Country, call `login_admin()` is done per-test (following OER pattern)
- Uses `baker.make` or direct `Title.objects.create` (matching existing patterns)

## Verification
```bash
make dev_test_app app=title
```
