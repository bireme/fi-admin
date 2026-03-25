# Plan: Unit Tests for Multimedia List Views

## Context

The multimedia app's `tests.py` has basic list view tests (`test_list_media`, `test_list_media_type`, `test_list_media_collection`) and one search test (`test_search_id`), but the `MultimediaListView.get_queryset()` method (views.py:37-77) contains substantial filtering logic that is largely untested: status filtering, thematic area filtering, user/CC filtering, collection filtering, ordering, owner filtering, and context data. The goal is to increase test coverage for these list view paths.

## Approach

Add a new test class `MultimediaListViewTest` in `src/multimedia/tests.py` with focused test methods for each filtering path in the base `MultimediaListView.get_queryset()` and `get_context_data()`. Follow the established pattern: use `BaseTestCase`, `baker.make()`, and `self.client.get()` with query parameters.

## File to Modify

- `src/multimedia/tests.py` — add new test class with list view filtering/context tests

## Existing Patterns to Reuse

- `BaseTestCase` from `utils/tests.py` — `login_editor()`, `login_documentalist()`, `login_admin()`
- `baker.make()` from `model_bakery` for creating `Media`, `MediaType`, `MediaCollection` objects
- `create_media_object()` helper already in tests.py
- `assertContains` / `assertNotContains` / `assertEqual` for assertions

## Test Cases to Add

### 1. Owner Filtering (`filter_owner`) — MediaListView

#### 1a. `test_media_list_default_filters_by_user`
- Login as editor, create media by editor and by another user
- GET `/multimedia/` (default, no filter_owner param)
- Assert only editor's media appears (restrict_by_user=True)

#### 1b. `test_media_list_filter_owner_all`
- Login as editor, create media by multiple users
- GET `/multimedia/?filter_owner=*`
- Assert all media records appear

### 2. Status Filtering

#### 2a. `test_media_list_filter_by_status`
- Create media with status=0 (Pending) and status=1 (Admitted)
- GET `/multimedia/?filter_status=1&filter_owner=*`
- Assert only admitted media appears

### 3. Thematic Area Filtering

#### 3a. `test_media_list_filter_by_thematic_area`
- Create media with associated ResourceThematic
- GET `/multimedia/?filter_thematic=<thematic_id>&filter_owner=*`
- Assert only media with matching thematic area appears

### 4. Created By User Filtering

#### 4a. `test_media_list_filter_by_created_by_user`
- Create media by two different users
- GET `/multimedia/?filter_created_by_user=<user_id>&filter_owner=*`
- Assert only media created by specified user appears

### 5. Cooperative Center Filtering

#### 5a. `test_media_list_filter_by_cc`
- Create media with different cooperative_center_code values
- GET `/multimedia/?filter_created_by_cc=BR1.1&filter_owner=*`
- Assert only media from BR1.1 appears

### 6. Search Functionality

#### 6a. `test_media_list_search_by_title`
- Create media with distinct titles
- GET `/multimedia/?s=<search_term>&filter_owner=*`
- Assert matching record appears, non-matching does not

#### 6b. `test_media_list_search_by_field`
- Create media with known title
- GET `/multimedia/?s=title:<value>&filter_owner=*`
- Assert field-specific search works (already partially covered by test_search_id, but test title field)

### 7. Ordering

#### 7a. `test_media_list_ordering`
- Create multiple media records
- GET `/multimedia/?order=-&orderby=title&filter_owner=*`
- Assert records appear in descending title order

### 8. Context Data

#### 8a. `test_media_list_context_data`
- GET `/multimedia/`
- Assert `response.context` contains: `actions`, `cc_filter_list`, `thematic_list`, `collection_list`, `show_advaced_filters`

### 9. Access Control

#### 9a. `test_media_list_unauthenticated_redirects`
- Logout, GET `/multimedia/`
- Assert redirect to login page

### 10. MediaTypeListView Tests

#### 10a. `test_media_type_list_requires_superuser`
- Login as editor (non-superuser)
- GET `/multimedia/media-types/`
- Assert 403

#### 10b. `test_media_type_list_superuser_access`
- Login as admin
- Create MediaType objects
- GET `/multimedia/media-types/`
- Assert 200 and objects appear

#### 10c. `test_media_type_list_no_user_restriction`
- Login as admin, create MediaType by another user
- GET `/multimedia/media-types/`
- Assert all types appear (restrict_by_user=False)

### 11. MediaCollectionListView Tests

#### 11a. `test_media_collection_list_filter_by_cc`
- Create collections with different CC codes
- GET `/multimedia/collections/?filter_created_by_cc=BR1.1`
- Assert only BR1.1 collections appear (already partially covered, but expand)

#### 11b. `test_media_collection_list_search`
- Create collections with distinct names
- GET `/multimedia/collections/?s=<search_term>`
- Assert matching collection appears

#### 11c. `test_media_collection_list_no_user_restriction`
- Login as editor, create collections by different users
- GET `/multimedia/collections/`
- Assert all collections appear (restrict_by_user=False)

### 12. Advanced Filters Flag

#### 12a. `test_show_advanced_filters`
- GET `/multimedia/?apply_filters=1`
- Assert `response.context['show_advaced_filters']` is truthy

## Test Class Structure

```
MultimediaListViewTest (new class)
  - test_media_list_default_filters_by_user (1a)
  - test_media_list_filter_owner_all (1b)
  - test_media_list_filter_by_status (2a)
  - test_media_list_filter_by_thematic_area (3a)
  - test_media_list_filter_by_created_by_user (4a)
  - test_media_list_filter_by_cc (5a)
  - test_media_list_search_by_title (6a)
  - test_media_list_search_by_field (6b)
  - test_media_list_ordering (7a)
  - test_media_list_context_data (8a)
  - test_media_list_unauthenticated_redirects (9a)
  - test_media_type_list_requires_superuser (10a)
  - test_media_type_list_superuser_access (10b)
  - test_media_type_list_no_user_restriction (10c)
  - test_media_collection_list_filter_by_cc (11a)
  - test_media_collection_list_search (11b)
  - test_media_collection_list_no_user_restriction (11c)
  - test_show_advanced_filters (12a)
```

Total: 18 new test methods covering all queryset filtering paths and context data.

## Verification

1. Run tests: `make dev_test_app app=multimedia`
2. Run coverage: `make dev_test_coverage` and check multimedia views coverage improvement
3. All new tests should pass with HTTP 200 responses and correct filtering behavior
