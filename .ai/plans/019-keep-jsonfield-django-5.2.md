# Plan 019 — Django Upgrade Phase 5.1: Keep `jsonfield`

## Context

Plan `001-upgrade-django-to-5.2.md` task 5.1 (decided 2026-09-28) keeps `jsonfield==3.2.0` through Django 5.2 rather than migrating to `models.JSONField`. The field is used 25 times across `biblioref`, `leisref`, `oer`, `multimedia` and `title`, and storage stays TEXT. That decision now needs evidence:

- migrations stay clean
- values round-trip unchanged
- the form/display behaviour is pinned by tests
- the same tests pass on Python 3.14

jsonfield 3.2.0 (2025-07-04, still the latest on PyPI as of 2026-10-06) declares Python only up to 3.13 and is marked "Inactive". No code under `src/utils/fields.py` changes.

### Findings from exploration
- **Hidden coupling:** jsonfield's `formfield()` passes the model field's **own** `dump_kwargs` dict to the form field. `utils.fields.JSONField.formfield()` then sets `indent=None` on it, which mutates the model field. All 16 migration files record `dump_kwargs={'ensure_ascii': False, 'indent': None}`. That means `makemigrations` is clean only because ModelForms get imported (via URL checks) before the autodetector runs. A test should pin this.
- `'' → '""'` and `None → NULL` (`null=True`) round-trip correctly by library design. `dumps_for_display()` has four branches (`None`, `'null'`, `''`, list, other string).
- **`utils` is missing from `src/run_tests.sh` and `src/run_coverage.sh`.** Its existing tests (Fieldset, DescriptorFormSet, GetFieldDisplay) never run in `make dev_test`.
- `multimedia.Media.description_translations` is the simplest host model. It only needs a `MediaType` plus `title` and `link`, and `multimedia/tests.py` already creates one this way.
- Other consumers: `api/tastypie_custom.py` (`CustomResource.api_field_from_django_field` → `JSONApiField`) and `utils/templatetags/app_filters.py:110` (`display_field` json.loads non-list values).

## Implementation steps

1. **Makefile: migration check.** Add a `dev_makemigrations_check` target that runs `python manage.py makemigrations --check --dry-run`, then run it. Expect "No changes detected". If it reports changes, stop and investigate; don't commit migrations blindly.

2. **Tests: `src/utils/tests.py`.** Add `JSONFieldTest(TestCase)`, built on `Media`/`MediaType` from `multimedia.models`:
   - Round-trip for a list (with non-ASCII text, e.g. `[{"text": "Ação", "_i": "pt"}]`), a dict, `None` and `''`. Each test calls `save()` then `refresh_from_db()` and asserts equality.
   - Raw storage read via `connection.cursor()`:
     - non-ASCII is stored unescaped (`ensure_ascii=False`)
     - `None` is stored as SQL NULL
     - the value has no newlines
   - Form field from `Media._meta.get_field('description_translations').formfield()`:
     - the widget is `HiddenInput` with `class="jsonfield"`
     - `prepare_value()` output has no `\n` (`indent=None`)
     - the rendered widget HTML has `type="hidden"`
   - `dumps_for_display()`:
     - `None`, `'null'` and `''` → `None`
     - a list → compact JSON string
     - a string → unchanged
   - Deconstruct guard: after `formfield()`, `field.deconstruct()[3]['dump_kwargs'] == {'ensure_ascii': False, 'indent': None}`. This matches the migrations, so any change to this coupling fails loudly.
   - API mapping: `CustomResource.api_field_from_django_field(field)` is `JSONApiField`.

3. **Test runners.** Add `utils` to `APPS` in `src/run_tests.sh` and `src/run_coverage.sh`. This turns on the existing utils tests too; if any of them fail, report it and fix only if trivial.

4. **Dockerfile: Python build arg.** Put `ARG PYTHON_VERSION=3.12` before the first stage and change it to `FROM python:${PYTHON_VERSION}-alpine AS base`. The default is unchanged, so normal builds are identical (check with `make dev_build`).

5. **Makefile: `dev_test_py` target**, a throwaway image on another Python version:
   ```make
   PY ?= 3.14
   PY_DJANGO ?= Django>=5.2.8,<5.3
   dev_test_py:
   	@docker build --target dev --build-arg PYTHON_VERSION=$(PY) -t $(IMAGE_NAME):py$(PY)-test .
   	@docker run --rm -v ./src:/app --env-file conf/app-env-dev $(IMAGE_NAME):py$(PY)-test \
   		sh -c 'pip install -q "$(PY_DJANGO)" && python -W ignore manage.py test -v 1 $(or $(app),utils)'
   ```
   The Django overlay is needed because 4.2 doesn't support 3.14. If another package such as haystack, rosetta or tinymce breaks app loading on Django 5.2, record it as a task 5.3 finding. Don't fix it here.
   - If the jsonfield tests pass on 3.14, mark plan task 5.2 as "3.14 confirmed".
   - If they fail because of jsonfield, update 5.2 and the risk registry to target `python:3.13-alpine`.

6. **Docs.**
   - In `001-upgrade-django-to-5.2.md` §5.1, tick the makemigrations, tests and 3.14 items. Leave the PyPI-watch item open with "checked 2026-10-06: 3.2.0 still latest".
   - Note the `dump_kwargs` coupling under §5.1.
   - Write `.ai/logs/2026-10-06-keep-jsonfield-phase5.1.md`.

## Critical files
- `src/utils/tests.py` (new `JSONFieldTest`)
- `src/run_tests.sh`, `src/run_coverage.sh` (add `utils`)
- `Makefile` (`dev_makemigrations_check`, `dev_test_py`)
- `Dockerfile` (`PYTHON_VERSION` build arg)
- `.ai/plans/001-upgrade-django-to-5.2.md`, `.ai/logs/…`
- Unchanged: `src/utils/fields.py`, `requirements.txt`

## Verification
- `make dev_build && make dev_up`: the image still builds on 3.12
- `make dev_makemigrations_check` → "No changes detected"
- `make dev_test_app app=utils`: the new tests pass
- `make dev_test`: full suite passes, ≥ 223 tests plus the new `utils` tests
- `make dev_test_py` (3.14 + Django 5.2): `utils` tests pass, or the failure is documented and the 3.13 fallback is recorded
