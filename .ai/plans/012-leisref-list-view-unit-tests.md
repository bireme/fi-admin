# Plan: Unit Tests for LeisRef List Views

## Context

The leisref app's `tests.py` has basic tests (`test_list_act`, `test_add_act`, `test_edit_act`, `test_delete_act`, `test_list_act_type`, `test_add_act_type`, `test_search_id`), but `LeisRefGenericListView.get_queryset()` (views.py:39-94) contains substantial filtering logic that is largely untested: status filtering, scope filtering, country filtering, indexed_database filtering, act_type filtering, collection filtering, ordering, owner filtering, and search by title/denomination. The goal is to increase test coverage for these list view paths, following the same approach used for multimedia (plan 010).

## File to Modify

- `src/leisref/tests.py` — add new test class `LeisRefListViewTest`

## Existing Patterns to Reuse

- `BaseTestCase` from `utils/tests.py` — `login_editor()`, `login_documentalist()`, `login_admin()`
- `create_act_object()` helper already in `leisref/tests.py`
- `ActCountryRegion.objects.create()`, `ActType.objects.create()` setup pattern from existing `setUp()`
- URL `/legislation/` maps to `LeisRefListView` (name: `list_legislation`)
- `settings.ACTIONS` keys: `filter_status`, `filter_scope`, `filter_country`, `filter_indexed_database`, `filter_act_type`, `filter_collection`, `filter_owner`, `s`, `order`, `orderby`

## Test Cases to Add

### New Class: `LeisRefListViewTest(BaseTestCase)`

**setUp:** Create `scope_region`, `act_type`, `thematic_area` (reuse existing pattern from `LeisRefTest.setUp`)

### 1. Owner Filtering (`filter_owner`)

#### 1a. `test_list_default_filters_by_user`
- Login as editor, create Act by editor and by another user (admin)
- GET `/legislation/` (default, no filter_owner)
- Assert only editor's Act appears (`restrict_by_user=True`)

#### 1b. `test_list_filter_owner_all`
- Login as editor, create Acts by multiple users
- GET `/legislation/?filter_owner=*`
- Assert all Act records appear

### 2. Status Filtering

#### 2a. `test_list_filter_by_status`
- Create Acts with status=-1 (Draft) and status=1 (Published)
- GET `/legislation/?filter_status=1&filter_owner=*`
- Assert only published Act appears

### 3. Scope Filtering

#### 3a. `test_list_filter_by_scope`
- Create ActScope, create Acts with and without that scope
- GET `/legislation/?filter_scope=<scope_id>&filter_owner=*`
- Assert only matching Act appears

### 4. Country/Region Filtering

#### 4a. `test_list_filter_by_country`
- Create Acts with different scope_region values
- GET `/legislation/?filter_country=<region_id>&filter_owner=*`
- Assert only matching Act appears

### 5. Indexed Database Filtering

#### 5a. `test_list_filter_by_indexed_database`
- Create Database object, create Act with that indexed_database M2M
- GET `/legislation/?filter_indexed_database=<db_id>&filter_owner=*`
- Assert only matching Act appears

### 6. Act Type Filtering

#### 6a. `test_list_filter_by_act_type`
- Create Acts with different act_type values
- GET `/legislation/?filter_act_type=<type_id>&filter_owner=*`
- Assert only matching Act appears

### 7. Collection Filtering

#### 7a. `test_list_filter_by_collection`
- Create Collection (from `classification.models`), associate via GenericRelation
- GET `/legislation/?filter_collection=<collection_id>&filter_owner=*`
- Assert only matching Act appears

### 8. Search Functionality

#### 8a. `test_list_search_by_act_number`
- Create Acts with distinct act_number values
- GET `/legislation/?s=<number>&filter_owner=*`
- Assert matching record appears (exact match on act_number)

#### 8b. `test_list_search_by_title`
- Create Acts with distinct titles
- GET `/legislation/?s=<title_fragment>&filter_owner=*`
- Assert title search works (icontains on title field)

#### 8c. `test_list_search_by_denomination`
- Create Acts with distinct denomination values
- GET `/legislation/?s=<denomination_fragment>&filter_owner=*`
- Assert denomination search works (icontains on denomination field)

#### 8d. `test_list_search_by_field_prefix`
- Create Act with known title
- GET `/legislation/?s=title:<value>&filter_owner=*`
- Assert field-specific search via colon syntax works

### 9. Ordering

#### 9a. `test_list_ordering`
- Create multiple Acts
- GET `/legislation/?order=-&orderby=title&filter_owner=*`
- Assert records appear in descending title order

### 10. Context Data

#### 10a. `test_list_context_data`
- GET `/legislation/`
- Assert `response.context` contains: `actions`, `user_role`, `scope_list`, `scope_region_list`, `indexed_database_list`, `collection_list`, `act_type_list`, `show_advaced_filters`

### 11. Access Control

#### 11a. `test_list_unauthenticated_redirects`
- Logout, GET `/legislation/`
- Assert redirect to login page

### 12. Advanced Filters Flag

#### 12a. `test_show_advanced_filters`
- GET `/legislation/?apply_filters=1`
- Assert `response.context['show_advaced_filters']` is truthy

### 13. Auxiliary List Views

#### 13a. `test_country_region_list_no_user_restriction`
- Login as admin, create ActCountryRegion by another user
- GET `/legislation/country-region/`
- Assert all regions appear (`restrict_by_user=False`)

#### 13b. `test_act_scope_list`
- Login as admin, create ActScope objects
- GET `/legislation/act-scope/`
- Assert 200 and objects appear

#### 13c. `test_act_type_list_no_user_restriction`
- Login as admin, create ActType by another user
- GET `/legislation/act-types/`
- Assert all types appear (`restrict_by_user=False`, `paginate_by=999`)

#### 13d. `test_act_organ_list`
- GET `/legislation/organs/`
- Assert 200

#### 13e. `test_act_source_list`
- GET `/legislation/sources/`
- Assert 200

#### 13f. `test_act_reltype_list`
- GET `/legislation/relation-types/`
- Assert 200

#### 13g. `test_act_state_list`
- GET `/legislation/act-states/`
- Assert 200

#### 13h. `test_act_city_list`
- GET `/legislation/act-cities/`
- Assert 200

#### 13i. `test_act_collection_list`
- GET `/legislation/act-collections/`
- Assert 200

## Test Class Structure

```
LeisRefListViewTest(BaseTestCase)
  setUp()
  test_list_default_filters_by_user (1a)
  test_list_filter_owner_all (1b)
  test_list_filter_by_status (2a)
  test_list_filter_by_scope (3a)
  test_list_filter_by_country (4a)
  test_list_filter_by_indexed_database (5a)
  test_list_filter_by_act_type (6a)
  test_list_filter_by_collection (7a)
  test_list_search_by_act_number (8a)
  test_list_search_by_title (8b)
  test_list_search_by_denomination (8c)
  test_list_search_by_field_prefix (8d)
  test_list_ordering (9a)
  test_list_context_data (10a)
  test_list_unauthenticated_redirects (11a)
  test_show_advanced_filters (12a)
  test_country_region_list_no_user_restriction (13a)
  test_act_scope_list (13b)
  test_act_type_list_no_user_restriction (13c)
  test_act_organ_list (13d)
  test_act_source_list (13e)
  test_act_reltype_list (13f)
  test_act_state_list (13g)
  test_act_city_list (13h)
  test_act_collection_list (13i)
```

Total: 25 new test methods covering all queryset filtering paths, search, ordering, context data, and auxiliary list views.

## Verification

1. Run tests: `make dev_test_app app=leisref`
2. Run coverage: `make dev_test_coverage` and check leisref views coverage improvement
3. All new tests should pass with HTTP 200 responses and correct filtering behavior
