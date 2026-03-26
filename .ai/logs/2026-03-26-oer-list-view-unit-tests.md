# OER List View Unit Tests

**Date:** 2026-03-26

## Summary

Added 12 new test methods in `OERListViewTest` class to `src/oer/tests.py`, covering all filtering paths in `OERGenericListView.get_queryset()` and `get_context_data()`.

## Changes

### `src/oer/tests.py`
- Added `OERListViewTest(BaseTestCase)` class with `_create_oer()` helper and 12 test methods:
  - **Owner filtering:** default user filter, filter_owner=center (cooperative center), filter_owner=* (all records)
  - **Status filtering:** filter_status parameter
  - **Country/CVSP node filtering:** filter_country parameter
  - **Search:** title icontains, field:value prefix syntax, empty search returns all
  - **Ordering:** descending sort with order/orderby params
  - **Context data:** verify expected context keys (actions, user_role, cvsp_node_list, show_advaced_filters)
  - **Access control:** unauthenticated redirect
  - **Advanced filters flag:** apply_filters parameter

## Test Results

All 17 tests pass (5 existing + 12 new).
