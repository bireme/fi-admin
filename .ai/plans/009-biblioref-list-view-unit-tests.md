# Plan: Unit Tests for BiblioRef List Views

## Context

The `BiblioRefListGet` test class in `src/biblioref/tests.py` currently has only 4 tests covering basic GET, template usage, status filtering, and deleted source exclusion. The `BiblioRefGenericListView.get_queryset()` method (views.py:53-245) contains substantial filtering logic that is untested: owner-based filtering, document type filtering, search, ordering, context data, and role-based access. The goal is to significantly increase test coverage for the list views.

## Approach

Expand the existing `BiblioRefListGet` class in `src/biblioref/tests.py` with new test methods covering all major queryset filtering paths and context data. Follow the established pattern: use `BaseTestCase`, `baker.make()` for object creation, and `self.client.get()` with query parameters.

## Files to Modify

- `src/biblioref/tests.py` — add new test methods to `BiblioRefListGet` and a new test class for source/analytic list views

## Existing Patterns to Reuse

- `BaseTestCase` from `utils/tests.py` — `login_documentalist()`, `login_editor()`, `login_editor_llxp()`, `login_admin()`
- `baker.make()` from `model_bakery` for creating `ReferenceSource`, `ReferenceAnalytic`, `Reference` objects
- `assertContains` / `assertNotContains` / `assertEqual` for assertions

## Test Cases to Add

### 1. Owner Filtering (`filter_owner`)

#### 1a. `test_filter_owner_user` — Default filter shows only current user's records
- Create references by two different users
- GET `/bibliographic/` (default `filter_owner=user`)
- Assert only current user's references appear

#### 1b. `test_filter_owner_center` — Filter by cooperative center
- Create references with different `cooperative_center_code` values
- GET with `filter_owner=center`
- Assert only records matching user's CC (`BR1.1`) appear

#### 1c. `test_filter_owner_all` — Show all records
- Create references by different users
- GET with `filter_owner=*`
- Assert all records appear

### 2. Document Type Filtering (`document_type`)

#### 2a. `test_filter_by_document_type`
- Create `ReferenceSource` with `literature_type='S'`, `treatment_level=''` (serial source)
- Create `ReferenceSource` with `literature_type='M'`, `treatment_level='m'` (monograph)
- GET with `document_type=S&filter_owner=*`
- Assert only serial source appears

#### 2b. `test_filter_by_analytic_document_type`
- Create `ReferenceAnalytic` with `literature_type='S'`, `treatment_level='as'`
- GET with `document_type=Sas&filter_owner=*`
- Assert analytic record appears

### 3. Status Filtering (expand existing)

#### 3a. `test_filter_status_draft`
- Create records with different statuses (-1 draft, 0 inprocess, 1 published)
- GET with `filter_status=-1&filter_owner=*`
- Assert only draft records appear (excluding serial sources per line 239-240)

#### 3b. `test_filter_status_published`
- GET with `filter_status=1&filter_owner=*`
- Assert only published records appear

### 4. Search Functionality

#### 4a. `test_search_by_title`
- Create references with distinct `reference_title` values
- GET with `s=<search_term>&filter_owner=*`
- Assert matching record appears, non-matching does not

#### 4b. `test_search_by_field_id`
- Create reference with known ID
- GET with `s=id:<id>&filter_owner=*`
- Assert exact record appears

### 5. Source/Analytic List Views

#### 5a. `test_list_sources_view`
- GET `/bibliographic/sources/`
- Assert HTTP 200

#### 5b. `test_list_analytics_view`
- Create a `ReferenceSource`, then `ReferenceAnalytic` linked to it
- GET `/bibliographic/analytics?source=<id>`
- Assert HTTP 200 and analytic appears

#### 5c. `test_list_analytics_filtered_by_source`
- Create two sources with analytics
- GET `/bibliographic/analytics?source=<id>`
- Assert only analytics from the specified source appear

### 6. Context Data

#### 6a. `test_context_contains_expected_keys`
- GET `/bibliographic/`
- Assert `response.context` contains: `actions`, `document_type`, `source_id`, `user_data`, `user_role`, `indexed_database_list`, `collection_list`

### 7. Access Control

#### 7a. `test_unauthenticated_user_redirected`
- Logout, GET `/bibliographic/`
- Assert redirect to login page

#### 7b. `test_editor_llxp_sources_filtered_by_center`
- Login as `editor_llxp` (CC=BR772)
- Create sources with different CC codes
- GET `/bibliographic/sources/`
- Assert only records with CC=BR772 appear (forced `filter_owner=center`)

### 8. Ordering

#### 8a. `test_custom_ordering`
- Create multiple references
- GET with `order=-&orderby=reference_title&filter_owner=*`
- Assert records appear in descending title order

### 9. Excluded Records

#### 9a. `test_draft_filter_excludes_serial_sources`
- Create a serial source (literature_type='S', treatment_level='') with status=-1
- Create an analytic (treatment_level='as') with status=-1
- GET with `filter_status=-1&filter_owner=*`
- Assert source is excluded, analytic appears

## Test Class Structure

```
BiblioRefListGet (existing, expand)
  - existing tests (4)
  - new owner filter tests (3)
  - new document type tests (2)
  - new status filter tests (2)
  - new search tests (2)
  - new context data test (1)
  - new access control test (1)
  - new ordering test (1)
  - new exclusion test (1)

BiblioRefSourceListGet (new class)
  - test_list_sources_view
  - test_editor_llxp_sources_filtered_by_center

BiblioRefAnalyticListGet (new class)
  - test_list_analytics_view
  - test_list_analytics_filtered_by_source
```

## Verification

1. Run tests: `make dev_test_app app=biblioref`
2. Run coverage: `make dev_test_coverage` and check biblioref views coverage improvement
3. All new tests should pass with HTTP 200 responses and correct filtering behavior
