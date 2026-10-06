# Plan 020 — Django Upgrade Phases 5.2 & 5.3: Python 3.14 + Django 5.2 dependency bumps

## Context

This plan covers tasks 5.2 and 5.3 of `001-upgrade-django-to-5.2.md`: moving the image to Python 3.14 and the pinned dependencies to Django 5.2. Phase 5.1 (commit `b50cc6c3`, not yet merged) laid the groundwork:
- it added `ARG PYTHON_VERSION=3.12` to the `Dockerfile` and the `make dev_test_py` target
- it showed the image builds on 3.14 (including mysqlclient and lxml) and that the `utils` tests pass on Django 5.2.18

The goal is a dev/prod image on `python:3.14-alpine` running Django 5.2.18, with every other dependency at a version that supports 5.2. Each bump should be isolated, so that any regression can be traced to one package.

### Decisions (2026-10-06)
- **Branch:** commit the pending edit to `001` on the 5.1 branch first. Then create `feature/django-upgrade-phase-5.2-5.3` from `feature/django-upgrade-phase-5.1-keep-jsonfield`.
- **mysqlclient:** stays at 2.2.8. It is already the latest 2.2.x, and it builds on 3.14.
- **Test failures caused by Django 5.x breaking changes (task 5.4) are recorded, not fixed.** The suite may stay red. The rule is **no new failures** from any bump after Django.

### Findings (PyPI, 2026-10-06)

| Package | Current | Target | Declared support |
|---|---|---|---|
| Django | 4.2.30 | **5.2.18** (latest 5.2.x) | Python 3.14 needs 5.2.8+ |
| django-haystack | 3.3.0 | **3.4.0** | Django 4.2/5.1/5.2, Python up to 3.14 |
| django-tinymce | 4.1.0 | **5.0.0** | Django 4.2–5.2, Python up to 3.13; bundles TinyMCE 7.8 |
| model-bakery (dev) | 1.17.0 | **1.24.2** | Django 5.2–6.1, Python up to 3.14 |
| lxml | 6.1.1 | **6.1.3** | Python up to 3.15 |
| django-rosetta | 0.10.3 | keep (no newer release) | Declares Django only up to 5.0 → smoke-test the UI |
| django-multiselectfield | 1.0.1 | keep (no newer release) | Declares Django only up to 5.1; used in `thesaurus/models_descriptors.py` and `models_qualifiers.py` |
| mysqlclient | 2.2.8 | keep | — |
| jsonfield / tastypie / debug-toolbar | 3.2.0 / 0.15.1 / 5.2.0 | keep | — |

- **TinyMCE caveat:** the editor JS loaded at runtime does not come from django-tinymce:
  - `settings.py` sets `TINYMCE_JS_URL = "/static/js/tinymce/tinymce.min.js"`, the project's own **TinyMCE 4.2.5**, with `theme: "modern"`.
  - That means django-tinymce's bundled TinyMCE is not used. Only its widget init JS changes.
  - The mismatch already exists on 4.1.0, which targets TinyMCE 6.
  - `HTMLField` is used in `help`, `institution` and `text_block`. A manual check that the editor still loads in their admin/forms is required.
  - Migrating to the bundled TinyMCE 7 is **out of scope**.
- Other pins (`gunicorn`, `pysolr`, `deform`, …) are not in the 5.3 table and are left alone.

## Implementation steps

0. **Branch setup.** On the 5.1 branch, commit the `001` edit (5.1 PyPI-watch tick, 5.3 table targets). Then `git checkout -b feature/django-upgrade-phase-5.2-5.3`.

1. **Django 4.2.30 → 5.2.18, still on Python 3.12.** Edit `requirements.txt`, then run `make dev_build && make dev_up`, `make dev_check` and `make dev_test`.
   - Save the output to the scratchpad. This is the **failure baseline**: every failing or erroring test is recorded by app and test name.
   - Doing Django on 3.12 first keeps Django breakages apart from Python 3.14 breakages.
   - Also run `make dev_makemigrations_check`. Record any non-JSONField changes for task 5.6; don't generate migrations here.

2. **Python 3.12 → 3.14 (task 5.2).** In the `Dockerfile`, set `ARG PYTHON_VERSION=3.14`. Run `make dev_build && make dev_up` and `make dev_test`, then compare against the baseline. Any new failure is a 3.14 issue. Fix it if it's trivial; if jsonfield-related, fall back to 3.13 per the risk registry.
   - Makefile `dev_test_py`: the `PY ?= 3.14` default now matches the image. Keep the target, which is still useful for trying other versions, but update its comment ("default: utils app on 3.14 + Django 5.2") so it doesn't suggest 3.14 is experimental.

3. **One package at a time** (task 5.3). For each package, edit the pin, then run `make dev_build && make dev_up` and `make dev_test`, comparing against the baseline:
   1. `django-haystack==3.4.0`. Also run `make dev_exec cmd="python manage.py shell -c 'from haystack import connections; connections[\"default\"].get_backend()'"`. A full `rebuild_index` is task 5.6.
   2. `django-tinymce==5.0.0`
   3. `lxml==6.1.3`
   4. `model-bakery==1.24.2` (`requirements-dev.txt`)

   If a bump introduces new failures that aren't trivial to fix, revert that pin to its last working version and record the reason in `001`.

4. **Smoke checks** (manual, `make dev_up`; logged in the plan/log rather than ticked as 5.6 verification):
   - Rosetta page `/rosetta/` loads
   - TinyMCE editor appears on a help/institution/text_block edit form
   - multiselectfield widgets on a thesaurus descriptor form render and save
   - `make api_build` succeeds, so the prod target builds on 3.14

5. **Docs.**
   - `001-upgrade-django-to-5.2.md`:
     - mark 5.2 done with the date
     - update the 5.3 table's "To" column to the final installed versions and mark rows done
     - add the recorded Django 5.2 test failures as a list under 5.4, each tagged with the matching 5.4 item, or as a new item
     - note the rosetta/multiselectfield "keep, not declared for 5.2" result
     - adjust the risk registry if the haystack or tastypie risk changes
   - Save this plan as `.ai/plans/020-upgrade-python-3.14-django-5.2-deps.md` and link it from `current-feature.md` `## Detailed Plan`.
   - Write the log `.ai/logs/2026-10-06-python-3.14-django-5.2-deps-phase5.2-5.3.md`: versions, baseline failures, per-bump results, smoke-check results.

## Critical files
- `Dockerfile`: the `PYTHON_VERSION` default
- `requirements.txt`, `requirements-dev.txt`: the pins
- `Makefile`: the `dev_test_py` comment only (existing targets cover everything else)
- `.ai/plans/001-upgrade-django-to-5.2.md`, `.ai/current-feature.md`, `.ai/logs/…`

## Verification
- `make dev_build` and `make api_build` succeed on `python:3.14-alpine`.
- `make dev_exec cmd="python --version"` prints 3.14.x, and `make dev_exec cmd="python -m django --version"` prints 5.2.18.
- `make dev_check` is clean.
- `make dev_test` shows no failures beyond the Django-5.2 baseline from step 1. The baseline itself is recorded in `001` §5.4 and the log.
- `make dev_test_app app=utils` passes (jsonfield round-trip tests from 5.1).
- The step 4 manual smoke checks pass.
