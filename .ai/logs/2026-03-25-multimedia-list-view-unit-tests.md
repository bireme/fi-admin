# Multimedia List View Unit Tests

**Date:** 2026-03-25

## Summary

Added 18 new unit tests for the multimedia list views (`MediaListView`, `MediaTypeListView`, `MediaCollectionListView`) in `src/multimedia/tests.py`.

## Changes

### File Modified
- `src/multimedia/tests.py` — added `MultimediaListViewTest` class with 18 test methods

### Test Coverage Added

| Category | Tests | Description |
|---|---|---|
| Owner filtering | 2 | Default user restriction and `filter_owner=*` |
| Status filtering | 1 | Filter by status code |
| Thematic area filtering | 1 | Filter by thematic area association |
| Created by user filtering | 1 | Filter by creator user ID |
| Cooperative center filtering | 1 | Filter by CC code |
| Search | 2 | Title search and field-specific search (`field:value`) |
| Ordering | 1 | Custom ordering by field |
| Context data | 1 | Verify expected context keys |
| Access control | 1 | Unauthenticated redirect |
| MediaType list | 3 | Superuser requirement, access, no user restriction |
| MediaCollection list | 3 | CC filter, search, no user restriction |
| Advanced filters | 1 | `apply_filters` flag in context |

### Test Results
- All 27 tests pass (9 existing + 18 new)
