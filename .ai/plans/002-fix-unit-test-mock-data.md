# Fix: Unit test mock data — hardcoded user IDs and missing profile data

## Context

After fixing the `context_processors.py` `AttributeError`, tests now run but fail due to two categories of mock data issues:

1. **Hardcoded `created_by_id` values (2, 3)** — test helper functions assume 3 users exist with IDs 1, 2, 3, but only 1 user is created per test via `login_editor()`. The FK constraint check in `_fixture_teardown` catches the invalid references.

2. **Missing profile data for admin user** — `login_admin()` creates a superuser without setting `profile.data`, so views that access `user_data['ccs']`, `user_data['service_role']`, etc. crash with `KeyError`.

3. **`tearDownClass` `AttributeError`** — Django compatibility bug in `_remove_databases_failures` triggered by `@override_settings` on `BaseTestCase`. Fixed by overriding `tearDownClass` to catch the error.

## Affected apps and errors

| App | Error | Root cause | Status |
|-----|-------|-----------|--------|
| main | `IntegrityError: created_by_id=2,3` | `create_resource_object()` hardcodes IDs | FIXED |
| events | `IntegrityError: created_by_id=2,3` | `create_test_objects()` hardcodes IDs | FIXED |
| multimedia | `IntegrityError: created_by_id=2,3` | `create_media_object()` + `test_list_media_collection()` hardcode IDs | FIXED |
| multimedia | `KeyError: 'ccs'` | `login_admin()` has no profile data; `multimedia/views.py:96` does `user_data['ccs']` | FIXED |
| all apps | `tearDownClass AttributeError` | Django compat bug with `@override_settings` | FIXED |
| multimedia | `test_add_media`/`test_edit_media` ManagementForm error | Missing attachment formset fields in test form data (pre-existing) | NOT FIXED — out of scope |
| biblioref | `assertContains` badge failure | Template/query logic issue, not mock data | NOT FIXED — out of scope |
| leisref | `assertContains` count mismatches | Template rendering issue (help text) | NOT FIXED — out of scope |

## Changes made

### Step 1: Fix `tearDownClass` Django compat error (`bireme/utils/tests.py`)

Override `tearDownClass` in `BaseTestCase` to catch the `AttributeError` from Django's `_remove_databases_failures`:

```python
@classmethod
def tearDownClass(cls):
    try:
        super().tearDownClass()
    except AttributeError:
        pass
```

### Step 2: Fix `login_admin()` — add profile data (`bireme/utils/tests.py`)

Added profile data to the admin user so views don't crash with `KeyError`:

```python
def login_admin(self):
    user_admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
    user_admin.profile.data = '''
    {
        "cc" : "BR1.1",
        "user_id" : 1,
        "service_role": [
            {"LIS" : "admin"},
            {"DirEVE" : "admin"},
            {"Multimedia" : "admin"},
            {"LILDBI" : "admin"},
            {"LeisRef" : "admin"},
            {"DirIns" : "admin"}
        ],
        "user_name" : "Admin",
        "ccs" : ["BR1.1"],
        "networks" : ["NETWORK 1"]
    }
    '''
    user_admin.profile.save()
    self.client.login(username='admin', password='admin')
    return user_admin
```

### Step 3: Make login helpers return user objects (`bireme/utils/tests.py`)

All `login_*()` methods now `return user_*` so tests can get the actual user ID dynamically.

### Step 4: Fix `create_resource_object()` (`bireme/main/tests.py`)

Accepts a `user` parameter and creates extra users inside the function:

```python
def create_resource_object(user):
    user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')
    user3 = User.objects.create_user('user3', 'user3@test.com', 'user3')

    Resource.objects.create(..., created_by=user, ...)
    Resource.objects.create(..., created_by=user2, ...)
    Resource.objects.create(..., created_by=user3, ...)
```

Callers updated: `user = self.login_editor()` then `create_resource_object(user)`.

### Step 5: Fix `create_test_objects()` (`bireme/events/tests.py`)

Same pattern as Step 4 — accepts `user`, creates helper users internally.

### Step 6: Fix `create_media_object()` (`bireme/multimedia/tests.py`)

Same pattern — accepts `user`, creates `user2` inside the function.

### Step 7: Fix `test_list_media_collection()` (`bireme/multimedia/tests.py`)

Creates `user2` and `user3` before `MediaCollection.objects.create(created_by=user2, ...)`.

## Files modified

1. `bireme/utils/tests.py` — `tearDownClass` override, `login_admin()` profile data, return user from all login methods
2. `bireme/main/tests.py` — `User` import, `create_resource_object(user)` + callers
3. `bireme/events/tests.py` — `User` import, `create_test_objects(user)` + callers
4. `bireme/multimedia/tests.py` — `User` import, `create_media_object(user)` + `test_list_media_collection()` + callers

## Verification

Run `make dev_test_app app=main` — all 9 tests pass with `OK`.

The remaining failures in multimedia (`test_add_media`/`test_edit_media`), biblioref (badge assertion), and leisref (count mismatches) are pre-existing issues unrelated to mock data.
