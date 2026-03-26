# Plan: Unit Tests for OER List Views

## Context

The OER app's `tests.py` has basic CRUD tests (`test_list_oer`, `test_add_oer`, `test_edit_oer`, `test_delete_oer`) and one search test (`test_search_id`), but `OERGenericListView.get_queryset()` (views.py:43-85) contains filtering logic that is largely untested: status filtering, cvsp_node/country filtering, ordering, owner filtering (user/center/*), and search by title. The `get_context_data()` context keys are also untested. The goal is to increase test coverage for these list view paths.

## File to Modify

- `src/oer/tests.py` — add new test class `OERListViewTest`

## Existing Patterns to Reuse

- `BaseTestCase` from `utils/tests.py` — `login_editor()`, `login_admin()`
- `create_oer_object()` helper already in `oer/tests.py`
- Existing `setUp()` pattern: creates `Type`, `SourceLanguage`, `License`, `LearningContext`, `ThematicArea`
- URL `/oer/` maps to `OERListView` (name: `list_oer`)

## Key Differences from LeisRef

OER's `filter_owner` logic is different (views.py:78-83):
- Default/`'user'` → filters by `created_by=request.user`
- `'center'` → filters by `cooperative_center_code=user_cc`
- `'*'` (any other value) → no user/center filter, shows all

OER search uses `__icontains` by default (not `__exact` like leisref), and only filters when search is non-empty (views.py:62-65).

## Test Cases to Add

### New Class: `OERListViewTest(BaseTestCase)`

**setUp:** Create `oer_type`, `language`, `license`, `learning_context`, `thematic_area` (reuse existing pattern)

### 1. Owner Filtering

#### 1a. `test_list_default_filters_by_user`
- Login as admin, create OER by admin and by another user
- GET `/oer/` (default filter_owner='user')
- Assert only admin's OER appears

#### 1b. `test_list_filter_owner_center`
- Login as admin (cc=BR1.1), create OER with cc=BR1.1 and cc=PY3.1
- GET `/oer/?filter_owner=center`
- Assert only BR1.1 OER appears

#### 1c. `test_list_filter_owner_all`
- Login as admin, create OERs by multiple users
- GET `/oer/?filter_owner=*`
- Assert all OER records appear

### 2. Status Filtering

#### 2a. `test_list_filter_by_status`
- Create OERs with status=-1 (Draft) and status=1 (Published)
- GET `/oer/?filter_status=1&filter_owner=*`
- Assert only published OER appears

### 3. Country/CVSP Node Filtering

#### 3a. `test_list_filter_by_country`
- Create OERs with different cvsp_node values
- GET `/oer/?filter_country=BR&filter_owner=*`
- Assert only matching OER appears

### 4. Search Functionality

#### 4a. `test_list_search_by_title`
- Create OERs with distinct titles
- GET `/oer/?s=Unique&filter_owner=*`
- Assert matching record appears (icontains on title)

#### 4b. `test_list_search_by_field_prefix`
- Create OER with known title
- GET `/oer/?s=title:Target&filter_owner=*`
- Assert field-specific search via colon syntax works

#### 4c. `test_list_empty_search_returns_all`
- Create multiple OERs
- GET `/oer/?s=&filter_owner=*`
- Assert all records appear (empty search = no filter)

### 5. Ordering

#### 5a. `test_list_ordering`
- Create multiple OERs
- GET `/oer/?order=-&orderby=title&filter_owner=*`
- Assert records appear in descending title order

### 6. Context Data

#### 6a. `test_list_context_data`
- GET `/oer/`
- Assert `response.context` contains: `actions`, `user_role`, `cvsp_node_list`, `show_advaced_filters`

### 7. Access Control

#### 7a. `test_list_unauthenticated_redirects`
- No login, GET `/oer/`
- Assert redirect (302)

### 8. Advanced Filters Flag

#### 8a. `test_show_advanced_filters`
- GET `/oer/?apply_filters=1`
- Assert `response.context['show_advaced_filters']` is truthy

## Test Class Structure

```
OERListViewTest(BaseTestCase)
  setUp()
  test_list_default_filters_by_user (1a)
  test_list_filter_owner_center (1b)
  test_list_filter_owner_all (1c)
  test_list_filter_by_status (2a)
  test_list_filter_by_country (3a)
  test_list_search_by_title (4a)
  test_list_search_by_field_prefix (4b)
  test_list_empty_search_returns_all (4c)
  test_list_ordering (5a)
  test_list_context_data (6a)
  test_list_unauthenticated_redirects (7a)
  test_show_advanced_filters (8a)
```

Total: 12 new test methods covering all queryset filtering paths and context data.

## Verification

1. Run tests: `make dev_test_app app=oer`
2. All new tests should pass
