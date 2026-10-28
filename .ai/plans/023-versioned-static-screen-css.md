# Plan 023 — Cache-busting version parameter for screen.css

## Context

`src/static/css/screen.css` changes often (sidebar/dashboard polish). nginx serves it from `/static/` without explicit cache headers, so browsers cache it heuristically and users keep seeing the old stylesheet after a deploy. Goal: load it as `css/screen.css?v=<hash>` where the hash changes only when the file's content changes.

Decisions (2026-10-28):
- **Custom template tag**, not `ManifestStaticFilesStorage`. Manifest was evaluated: collectstatic would fail on dangling CSS refs (`../image/logo-BIREME.png`, 7 jquery-ui icons, 3 `.map` files), gunicorn starts before `prod_exec_collectstatic` and reads the manifest once per worker, and tests (DEBUG=False) would need a storage override. Too much deploy churn for the goal.
- No new dependency: stdlib `hashlib` + `django.contrib.staticfiles.finders`.
- Generic tag (any static path), but only the 3 `screen.css` links switch to it now.
- Docker is the only deploy target; fabfile ignored.

## Implementation

### 1. New tag library `src/utils/templatetags/versioned_static.py`

```python
import hashlib
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


def file_hash(path):
    """Short md5 of a static file's content, or None if the file is not found."""
    absolute_path = finders.find(path)
    if not absolute_path:
        return None
    with open(absolute_path, 'rb') as f:
        return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()[:8]


cached_file_hash = lru_cache(maxsize=None)(file_hash)


@register.simple_tag
def versioned_static(path):
    """
    Static URL with a content-hash query string (?v=...), so browsers fetch the
    file again when it changes. Hash is cached per process; recomputed on every
    call when DEBUG is on so edits show up without restarting runserver.
    """
    digest = file_hash(path) if settings.DEBUG else cached_file_hash(path)
    url = static(path)
    return f'{url}?v={digest}' if digest else url
```

- Hash is read from the source file via finders (`STATICFILES_DIRS` → `src/static`, present in the image at build time), which matches what collectstatic copies to `STATIC_ROOT`.
- Missing file → plain `{% static %}` URL, no error.

### 2. Templates (3 files)

`src/templates/base.html`, `src/templates/suggest/invalid-link.html`, `src/templates/suggest/thanks.html`:

- add `{% load versioned_static %}` next to `{% load static %}`
- `<link href="{% static "css/screen.css" %}" ...>` → `<link href="{% versioned_static "css/screen.css" %}" ...>`

### 3. Tests — `src/utils/tests.py`

New `VersionedStaticTest(SimpleTestCase)`:
- renders `{% load versioned_static %}{% versioned_static "css/screen.css" %}` → matches `^/static/css/screen\.css\?v=[0-9a-f]{8}$`, and the hash equals md5 of `src/static/css/screen.css`[:8]
- nonexistent path → `/static/missing.css` (no `?v=`)
- `override_settings(DEBUG=True)` + patched `file_hash` content change → new value (no stale cache in dev); clear `cached_file_hash.cache_clear()` in `setUp`

### 4. Feature bookkeeping

- Save this plan as `.ai/plans/023-versioned-static-screen-css.md`; link it under `## Detailed Plan` in `.ai/current-feature.md`; update Notes with the Manifest decision
- Log `.ai/logs/2026-10-28-versioned-static-screen-css.md` after implementation

## Verification

- `make dev_test_app app=utils` — new tests pass
- `make dev_test` — full suite green
- `make dev_check` — clean
- Dev browser: page source shows `/static/css/screen.css?v=xxxxxxxx`; edit `screen.css`, reload → value changes
- Optional prod smoke: `make prod_build`, `prod_up`, `prod_exec_collectstatic`, curl page → versioned link; `curl /static/css/screen.css?v=...` served by nginx (query string ignored by `alias`)
