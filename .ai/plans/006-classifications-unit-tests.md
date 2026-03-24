# Plan: Unit Tests for `classify` View in Classification App

## Context

The classification app has no tests. Recent commits added CRUD unit tests for `title`, `oer`, and `leisref` apps following a consistent pattern using `BaseTestCase`. This plan adds unit tests for the `classify` view function in `src/classification/views.py`.

The `classify` view:
- Accepts `ctype_id` and `obj_id` URL parameters
- On POST: creates `Relationship` objects for items in `set` list, deletes for `unset` list
- Deduplicates both lists
- Returns a rendered template with `relation_list`, `community_list`, `c_type`, `object_id`, `relation_list_ids`, and `updated` flag

## Files to Create/Modify

- **Create**: `src/classification/tests.py` — new test file
- **Verify**: `Makefile` — confirm `dev_test_app` target works for classification

## Test Cases for `classify`

### ClassifyTest (extends BaseTestCase)

**setUp:**
- Login as admin via `self.login_admin()`
- Create a `Collection` (community, no parent) and a child `Collection`
- Get a `ContentType` to use as `ctype_id` (can use ContentType for Collection itself or any model)

**Tests:**

1. **`test_classify_get`** — GET request renders the template with empty relation list and community list
2. **`test_classify_set_relationship`** — POST with `set` list creates Relationship objects, response contains updated=True context
3. **`test_classify_unset_relationship`** — POST with `unset` list deletes existing Relationships
4. **`test_classify_set_and_unset`** — POST with both `set` and `unset` in same request
5. **`test_classify_set_duplicates`** — POST with duplicate IDs in `set` list creates only one Relationship (deduplication)
6. **`test_classify_unset_nonexistent`** — POST with `unset` for non-existent relationship doesn't error
7. **`test_classify_get_or_create_existing`** — POST `set` with already-existing relationship doesn't create duplicate

### GetChildrenListTest (extends BaseTestCase)

1. **`test_get_children_community`** — returns community-flagged children with type='community'
2. **`test_get_children_collection`** — returns non-community children with type='collection' when no community-flagged exist
3. **`test_get_children_empty`** — returns empty list and empty type when no children exist
4. **`test_get_children_sorted`** — children are returned sorted by name

## Implementation Approach

Follow the project's existing test patterns:
- Extend `BaseTestCase` from `utils.tests`
- Use `baker.make()` from `model_bakery` for creating test objects
- Use `self.client.get()` / `self.client.post()` for view requests
- URL pattern: `/classification/classify/<ctype_id>/<obj_id>/` and `/classification/get-children-list/<parent_id>/`

```python
# Key setup pattern:
from utils.tests import BaseTestCase
from classification.models import Collection, Relationship
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

class ClassifyTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.login_admin()
        self.community = Collection.objects.create(name='Test Community', language='en', community_flag=True)
        self.collection = Collection.objects.create(name='Test Collection', language='en', parent=self.community)
        # Use ContentType of Collection itself as the ctype
        self.ctype = ContentType.objects.get_for_model(Collection)
        self.obj_id = 1  # arbitrary object ID for testing
```

## Key Files Reference

- `src/classification/views.py` — the classify and get_children_list views
- `src/classification/models.py` — Collection, CollectionLocal, Relationship models
- `src/classification/urls.py` — URL patterns
- `src/utils/tests.py` — BaseTestCase with login helpers
- `src/title/tests.py` — reference pattern for test structure

## Verification

1. Run: `make dev_test_app app=classification`
2. All tests should pass
3. Create log file at `.ai/logs/2026-03-24-classification-unit-tests.md`
