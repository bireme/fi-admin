# 2026-10-06 — Django Upgrade Phase 5.1: Keep `jsonfield`

Branch: `feature/django-upgrade-phase-5.1-keep-jsonfield` · Plan: [019-keep-jsonfield-django-5.2.md](../plans/019-keep-jsonfield-django-5.2.md) (task 5.1 of [001](../plans/001-upgrade-django-to-5.2.md))

## Summary

We keep `jsonfield==3.2.0` through Django 5.2. No changes to `src/utils/fields.py` or `requirements.txt`, and no schema or data migration. This change adds the evidence for that decision: a migration check, tests that pin the field's behaviour, and a test run on Python 3.14 with Django 5.2.

## Changes

- **`Makefile`**
  - `dev_makemigrations_check`: `makemigrations --check --dry-run [app]`
  - `dev_test_py`: builds a throwaway `bireme/fi-admin:py$(PY)-test` image (default `PY=3.14`), installs `PY_DJANGO` (default `Django>=5.2.8,<5.3`) on top, and runs `manage.py test $(app)` (default `utils`). It needs `make dev_up`, because it joins the `nginx-proxy` network to reach memcached. It strips inline `# comments` from `conf/app-env-dev` into a temp env file, because `docker run --env-file` keeps them (Compose doesn't)
- **`Dockerfile`**: `ARG PYTHON_VERSION=3.12` + `FROM python:${PYTHON_VERSION}-alpine`. The default is unchanged (dev image still on Python 3.12.15)
- **`src/utils/tests.py`**: new `JSONFieldTest` (9 tests, using `multimedia.Media.description_translations`):
  - round-trip for a list (non-ASCII), a dict, `None` (stored as SQL NULL) and `''` (stored as `""`)
  - raw storage is compact JSON with non-ASCII unescaped
  - form field: `HiddenInput` with `class="jsonfield"`, `indent=None`, no newlines
  - `dumps_for_display()` branches
  - `deconstruct()` matches the migrations (`{'ensure_ascii': False, 'indent': None}`)
  - Tastypie maps the field to `JSONApiField`
- **`src/run_tests.sh`, `src/run_coverage.sh`**: added `utils` to `APPS`. Its existing tests (Fieldset, DescriptorFormSet, GetFieldDisplay) were never run by `make dev_test` before; all pass
- **`.ai/plans/001-upgrade-django-to-5.2.md`**:
  - ticked the §5.1 items, and added a note on the `dump_kwargs` coupling
  - left the PyPI-watch item open (checked today: 3.2.0 is still the latest)
  - §5.2 now targets 3.14 through the build arg
  - downgraded the jsonfield/3.14 risk

## Finding: `dump_kwargs` coupling

jsonfield's `formfield()` passes the model field's own `dump_kwargs` dict to the form field. `utils.fields.JSONField.formfield()` then sets `indent=None` on it, which mutates the model field. That's why all 16 migration files record `dump_kwargs={'ensure_ascii': False, 'indent': None}`. `makemigrations` is clean only because ModelForms are built (through URL checks) before the autodetector runs. The behaviour is left as is, and the new deconstruct test guards it.

## Verification

- `make dev_build && make dev_up`: OK on Python 3.12.15
- `make dev_makemigrations_check` → "No changes detected"
- `make dev_test_app app=utils` → 22 tests OK
- `make dev_test` → all apps OK, 247 tests (skipped=5), up from 223 since `utils` now runs
- `make dev_test_py` → Python 3.14.8 + Django 5.2.18: 22 `utils` tests OK. The image (mysqlclient, lxml) builds on 3.14, so the 3.13 fallback isn't needed
