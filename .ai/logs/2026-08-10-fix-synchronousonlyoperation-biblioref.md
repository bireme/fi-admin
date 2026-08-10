# Fix SynchronousOnlyOperation on /bibliographic/new-source

## Error

```
django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
  File "/app/biblioref/views.py", line 416, in form_valid
    asyncio.run(update_services(self.object))
  File "/app/biblioref/views.py", line 861, in update_reference_title
    for analytic in analytic_list:
```

## Analysis

`BiblioRefUpdate.form_valid()` ran the secondary updates with
`asyncio.run(update_services(obj))`. `update_services` was an `async def` that
dispatched three coroutines with `asyncio.create_task` + `asyncio.gather`.

All three coroutines use the Django ORM, which refuses to open a DB connection
from an event loop:

- `update_reference_title` — `ReferenceAnalytic.objects.filter(source=obj.id)`
  is evaluated by the `for` loop, which is **outside** the inner `try/except`,
  so the exception escaped to the view and produced the 500.
- `update_dedup_service` — `obj.document_type()` / `obj.source.*` (related field
  access triggers a query).
- `update_search_index` — `hasattr(reference, 'source')` and the haystack index
  serialization of related fields.

The error surfaced on a source record (`literature_type == 'S'` and no `source`)
that already had analytics attached — exactly the branch that queries analytics.

Root cause of the design: the three functions are **entirely blocking** —
`requests.post` and haystack `update_object` are sync calls with no `await`
points. The coroutines therefore never yielded control and ran sequentially
anyway: the async wrapper provided zero concurrency and only broke ORM access.
Every other app in the project (`main`, `events`, `leisref`, `oer`,
`institution`, `multimedia`) defines these same helpers as plain sync functions.

## Changes

- `src/biblioref/views.py`
  - `update_services`, `update_search_index`, `update_dedup_service` and
    `update_reference_title` converted from `async def` to plain functions.
  - `update_services` now calls the three helpers sequentially (same effective
    ordering as before) with a comment explaining why they must stay sync.
  - Call sites updated: `BiblioRefUpdate.form_valid` and
    `BiblioRefDeleteView.delete` no longer wrap them in `asyncio.run`.
  - Removed the now unused `import asyncio`.

- `src/biblioref/tests.py`
  - New `UpdateServicesTest` with a source + one analytic:
    - `test_update_reference_title_of_analytics` — calls `update_services` and
      asserts the analytic `reference_title` is updated to
      `"<source title> | <analytic title>"`. Reproduced the bug: with the async
      code, running it through `asyncio.run` raised `SynchronousOnlyOperation`
      with the exact production traceback.
    - `test_update_search_index_delete_of_source` — covers the delete path of
      `update_search_index`.
  - `biblioref.views` is imported inside the test methods because the module
    hits the database at import time (`field_definitions`), which fails during
    test collection.

## Verification

```
make dev_test_app app=biblioref
Ran 29 tests in 2.958s
OK (skipped=5)
```
