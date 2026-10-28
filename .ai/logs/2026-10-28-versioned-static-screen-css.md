# Cache-busting version parameter for screen.css

Date: 2026-10-28
Branch: `feature/cache-busting-version-parameter-for-screen-css` (from `feature/sidebar-menu-and-dashboard-polish`)
Plan: [023-versioned-static-screen-css.md](../plans/023-versioned-static-screen-css.md)

## Problem

nginx serves `/static/` without explicit cache headers, so browsers cache `css/screen.css` heuristically and users kept seeing the old stylesheet after a deploy.

## Changes

- `src/utils/templatetags/versioned_static.py` (new): `{% versioned_static path %}` returns the `{% static %}` URL plus `?v=<first 8 chars of the file's md5>`.
  - File located with `django.contrib.staticfiles.finders`; stdlib `hashlib`, no new dependency.
  - Hash cached per process (`lru_cache`); recomputed on every call when `DEBUG` is on, so CSS edits show up in dev without a restart.
  - File not found → plain static URL, no error.
- `src/templates/base.html`, `src/templates/suggest/thanks.html`, `src/templates/suggest/invalid-link.html`: load the library and use `{% versioned_static "css/screen.css" %}`.
- `src/utils/tests.py`: `VersionedStaticTest` (4 tests) — URL equals md5 of the real file, missing-file fallback, cached when not DEBUG, recomputed when DEBUG.

## Decision: not ManifestStaticFilesStorage

Evaluated and rejected: collectstatic post-processing would fail on dangling CSS references (`screen.css` → `../image/logo-BIREME.png`, 7 jquery-ui icon PNGs, 3 missing `.map` files); gunicorn starts before `make prod_exec_collectstatic` and loads the manifest once per worker; tests run with `DEBUG=False` and would need a storage override.

## Verification

- `make dev_test_app app=utils`: 26 tests OK
- `make dev_test`: all apps OK (253 tests, 5 skipped; was 249)
- `make dev_check`: not run successfully — dev DB `172.17.1.20` unreachable (`OperationalError 2002`), unrelated to this change
- Browser check of the rendered link not done (dev server not responding, same DB issue); templates using `base.html` are rendered by the passing view tests

## Deploy note

The hash is read from the source file in the image (`/app/static`), the same content collectstatic copies to `STATIC_ROOT`, so no deploy step changes. Releases where `screen.css` is unchanged keep the same URL and stay cached.
