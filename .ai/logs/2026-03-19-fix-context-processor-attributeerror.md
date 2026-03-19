# Fix: context_processors.py AttributeError on request.user

## Changes

**File**: `bireme/utils/context_processors.py`

Three fixes in `additional_user_info()`:

1. **Line 11**: `request.user` -> `getattr(request, 'user', None)` — safe access when `AuthenticationMiddleware` hasn't set `.user`
2. **Line 12**: `user_info = ''` -> `user_info = {}` — context processors must return a dict, not a string
3. **Line 22**: `if user.is_authenticated` -> `if user and user.is_authenticated` — guard against `None` user
4. **Line 24**: `cache.get(user_info_ck)` -> `cache.get(user_info_ck) or {}` — ensure cache miss doesn't set `user_info` to `None`

## Result

- The `TypeError: 'NoneType' object is not iterable` errors from `debug_toolbar` template panel are resolved
- The `AttributeError: 'HttpRequest' object has no attribute 'user'` is resolved
- Remaining test failures in `events.tests.EventTest` are pre-existing `IntegrityError` issues with test fixture foreign keys (unrelated)
