# LeisRef List View Unit Tests

**Date:** 2026-03-26

## Summary

Added 25 new test methods in `LeisRefListViewTest` class to `src/leisref/tests.py`, covering all filtering paths in `LeisRefGenericListView.get_queryset()` and `get_context_data()`.

## Changes

### `src/leisref/tests.py`
- Added import for `Collection` and `Relationship` from `classification.models`
- Added `LeisRefListViewTest(BaseTestCase)` class with 25 test methods:
  - **Owner filtering:** default user filter, filter_owner=* for all records
  - **Status filtering:** filter_status parameter
  - **Scope filtering:** filter_scope parameter
  - **Country/Region filtering:** filter_country parameter
  - **Indexed database filtering:** filter_indexed_database parameter (M2M)
  - **Act type filtering:** filter_act_type parameter
  - **Collection filtering:** filter_collection parameter (GenericRelation)
  - **Search:** act_number exact match, title icontains, denomination icontains, field:value prefix syntax
  - **Ordering:** descending sort with order/orderby params
  - **Context data:** verify all expected context keys
  - **Access control:** unauthenticated redirect
  - **Advanced filters flag:** apply_filters parameter
  - **Auxiliary list views:** country_region, act_scope, act_type, act_organ, act_source, act_reltype, act_state, act_city, act_collection (9 tests)

## Test Results

All 32 tests pass (7 existing + 25 new).
