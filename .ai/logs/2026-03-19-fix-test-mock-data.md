# Fix: Unit test mock data — hardcoded user IDs and missing profile data

## Date: 2026-03-19

## Problem
Tests were failing due to:
1. Hardcoded `created_by_id=2,3` in test helper functions when only 1 user existed
2. Missing `profile.data` on admin user causing `KeyError: 'ccs'` in views

## Changes

### `bireme/utils/tests.py`
- Added profile data (with ccs, service_role, networks, etc.) to `login_admin()`
- All login methods (`login_documentalist`, `login_editor`, `login_editor_llxp`, `login_admin`) now return the created user object

### `bireme/main/tests.py`
- Added `User` import
- `create_resource_object()` now accepts a `user` parameter and creates `user2`/`user3` internally
- Updated 3 callers to pass `user = self.login_editor()` result

### `bireme/events/tests.py`
- Added `User` import
- `create_test_objects()` now accepts a `user` parameter and creates `user2`/`user3` internally
- Updated 3 callers to pass `user = self.login_editor()` result

### `bireme/multimedia/tests.py`
- Added `User` import
- `create_media_object()` now accepts a `user` parameter and creates `user2` internally
- `test_list_media_collection()` creates `user2`/`user3` before using them
- Updated 3 callers to pass `user = self.login_editor()` result

## Results
- All main, events, and multimedia mock-data-related test failures are resolved
- Remaining issues (not mock data, out of scope):
  - `tearDownClass` `AttributeError` — Django compatibility issue
  - `test_add_media`/`test_edit_media` — missing attachment formset fields (pre-existing)
  - `biblioref` badge assertion — template/query logic issue
  - `leisref` assertion mismatches — template rendering issue
