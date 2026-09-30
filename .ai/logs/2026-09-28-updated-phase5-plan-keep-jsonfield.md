# 2026-09-28 — Updated Phase 5 of Django upgrade plan (keep `jsonfield`)

**File changed**: `.ai/plans/001-upgrade-django-to-5.2.md`

## Summary
Rewrote Phase 5 (Django 4.2 → 5.2 LTS, Python 3.12 → 3.14) to match the current state of the repo and to keep the `jsonfield` package, continuing the decision from task 4.1.

## Changes
- **5.0 Pre-flight (new)**: check DB versions (MySQL ≥ 8.0.11 / MariaDB ≥ 10.5), check for legacy password hashes whose hashers were removed in Django 5.1, and fix deprecation warnings on 4.2.
- **5.1 Keep `jsonfield` (new)**: no migration to native `models.JSONField`; `src/utils/fields.py` stays unchanged. Adds round-trip and form tests, and a check on Python 3.14 (jsonfield 3.2.0 declares support only up to 3.13), with `python:3.13-alpine` as the fallback.
- **5.2 Python version**: Dockerfile bump to 3.14 (or 3.13).
- **5.3 Dependencies**: corrected the "From" versions to match `requirements.txt` / `requirements-dev.txt`. Django must be ≥ 5.2.8 for Python 3.14.
- **5.4 Breaking changes**: added the removal of GET logout (`src/biremelogin/urls.py` `LogoutView`), the password hasher removals, `Model.save()` positional args, removed test/utility APIs, and storage settings.
- **5.5 Tastypie**: a concrete evaluation and fallback order (patch → fork → DRF as its own project).
- **5.6 Migrations/test** and an expanded verification checklist.
- Risk Registry: added rows for jsonfield on Python 3.14 and for the DB server minimum versions.
- Critical Files: updated the `src/utils/fields.py` entry and added `src/biremelogin/urls.py`.

No code or dependency changes.
