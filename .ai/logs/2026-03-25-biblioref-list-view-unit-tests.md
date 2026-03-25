# BiblioRef List View Unit Tests

**Date**: 2026-03-25

## Summary

Added 17 new unit tests for the BiblioRef list views in `src/biblioref/tests.py` to increase coverage of `BiblioRefGenericListView.get_queryset()` and related view classes.

## Changes

### File: `src/biblioref/tests.py`

**Expanded `BiblioRefListGet` class** (14 new tests):
- `test_filter_owner_user` - Default filter shows only current user's records
- `test_filter_owner_center` - Filter by cooperative center code
- `test_filter_owner_all` - Show all records with `filter_owner=*`
- `test_filter_by_document_type` - Filter by literature_type + treatment_level (Mm)
- `test_filter_by_analytic_document_type` - Filter analytic records (Sas)
- `test_filter_status_draft` - Draft filter excluding serial sources
- `test_filter_status_published` - Published status filter
- `test_search_by_title` - Title search using `__icontains` (with `FULLTEXT_SEARCH=False`)
- `test_search_by_field_id` - Field-specific `id:` search
- `test_context_contains_expected_keys` - Context data validation
- `test_unauthenticated_user_redirected` - Access control redirect
- `test_custom_ordering` - Descending order by field
- `test_draft_filter_excludes_serial_sources` - Draft filter exclusion logic

**New `BiblioRefSourceListGet` class** (2 tests):
- `test_list_sources_view` - HTTP 200 for sources list
- `test_editor_llxp_sources_filtered_by_center` - LLXP editor CC-based filtering

**New `BiblioRefAnalyticListGet` class** (2 tests):
- `test_list_analytics_view` - HTTP 200 and content for analytics list
- `test_list_analytics_filtered_by_source` - Source-based filtering of analytics

## Notes

- Search tests use `@override_settings(FULLTEXT_SEARCH=False)` because the test database runs on MySQL with `FULLTEXT_SEARCH=True`, but the fulltext index may not be available on the test database schema.
- Analytics and source records require proper `title`, `title_serial`, `volume_serial`, `issue_number`, and `publication_date_normalized` fields for the `__str__` methods to work in templates.
- All 21 list view tests pass (4 existing + 17 new).
