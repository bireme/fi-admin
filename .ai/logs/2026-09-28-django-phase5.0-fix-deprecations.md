# 2026-09-28 — Phase 5.0: fix Django 5.x deprecations on Django 4.2

**Spec**: `.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md`
**Branch**: `setup/django-5.2` (Django stays on 4.2.30, Python 3.12)

## Summary

Removed every deprecation warning that the code base itself produces on Django 4.2, ahead of the Django 5.2 bump. Full suite: **225 tests OK (skipped=5)**, up from 223 (2 new logout tests).

## Changes

| File | Change | Warning fixed |
|------|--------|---------------|
| `src/fi-admin/settings.py:9` | `DEBUG_TOOLBAR` is forced off when `test` is in `sys.argv`. The flag is set here because the `if 'test'` block runs after the toolbar is registered at line ~380 | `RemovedInDjango50Warning` form `default.html` (from debug-toolbar 4.3.0 panel forms, not app code). The suite also got faster: ~30s → ~7s |
| `requirements-dev.txt` | `django-debug-toolbar` 4.3.0 → 5.2.0 (declares Django 4.2–5.2) | — |
| `requirements.txt` | `django-tastypie` 0.14.7 → 0.15.1 (declares Django 4.2–5.2). The 0.15.0 PATCH change (#1617) doesn't reach our code: no resource allows PATCH | see "Remaining" |
| `Dockerfile` | `pip install --upgrade pip "setuptools<81"`: deform 3.0.1 (latest) imports `pkg_resources`, which setuptools 81 removes | protects the build (warning kept) |
| `src/templates/menu.html` | Logout link → POST `<form class="logout-form">` with `{% csrf_token %}` | `RemovedInDjango50Warning` logout via GET (tests didn't catch it) |
| `src/static/css/screen.css` | `.logout-form` button styled like a Bootstrap 2.0.4 `.dropdown-menu a` (no `.btn-link` in 2.0.4) | — |
| `src/main/tests.py` | New `LogoutTest`: the menu renders the POST form, and POST `/logout/` redirects to `/` and clears the session | — |
| `src/biblioref/tests.py` | 35 `created_time="1970-01-01 00:00"` → `EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)` | `RuntimeWarning` naive datetime |
| `src/institution/views.py` | Per-user branch of `InstGenericListView.get_queryset()` gets `.order_by('-id')`, the same default as the other branch | `UnorderedObjectListWarning` |
| `.ai/plans/001-upgrade-django-to-5.2.md` | Ticked 5.0 deprecations and 5.4 logout; marked tastypie/debug-toolbar as done early in 5.3/5.5 | — |

## Verification

- `make dev_build && make dev_up`: image built; setuptools 80.10.2, tastypie 0.15.1, debug-toolbar 5.2.0, Django 4.2.30
- `make dev_test`: 13 apps, 225 tests, all OK
- `make dev_test_deprecations app="main events multimedia biblioref leisref institution oer title thesaurus suggest classification error_reporting api"`: 225 OK. The warnings left are listed below
- Debug toolbar outside tests (`DEBUG=1 DEBUG_TOOLBAR=1`): app and middleware are loaded, the `debug_toolbar` system checks pass, and `djdt:render_panel` resolves. It was not checked in a browser

## Remaining warnings

1. `RemovedInDjango50Warning`, `tastypie/compat.py:22` `django.utils.datetime_safe`: **expected on 4.2 and can't be fixed on our side.** tastypie 0.15.1 imports it only when `django.VERSION < (5, 0)` and uses stdlib `datetime` on 5.x, so it disappears with the Django 5.2 bump. It was not silenced with a filter. The spec assumed the bump would remove this warning; it didn't.
2. `UserWarning`, `deform/template.py:7` `pkg_resources` deprecated: upstream (deform 3.0.1 is the latest release). The build is safe because of the `setuptools<81` pin. Watch for a deform release that drops `pkg_resources`.

## Manual checks still to do (validation env)

- Logout from the user dropdown: the button looks like the other menu items, and a click logs out and goes to `/`
- The debug toolbar renders in the browser with `DEBUG_TOOLBAR=1`
