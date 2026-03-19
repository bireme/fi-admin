# Phase 1.1 & 1.2 — Test Infrastructure & model-bakery Migration

**Date**: 2026-03-19
**Plan**: `.ai/plans/001-upgrade-django-to-5.2.md`

## 1.1 — Improve test infrastructure

### Changes

- **`requirements-dev.txt`**: Added `coverage==5.5` (compatible with Python 3.7)
- **`.coveragerc`**: Created coverage configuration file
  - Source: current directory
  - Omits: migrations, tests, settings, wsgi, manage.py
  - HTML report output to `htmlcov/`
- **`bireme/run_tests.sh`**: Updated to run ALL 21 project apps (was only 5: main, events, suggest, multimedia, biblioref)
- **`Makefile`**: Added two new targets:
  - `test` — runs all app tests via `manage.py test` (this is what `dev_test`, `api_make_test`, `prod_make_test` call inside the container)
  - `test_coverage` — runs tests with coverage, generates report + HTML
  - `dev_coverage` — docker-compose wrapper to run `test_coverage` inside dev container

## 1.2 — Replace model-mommy with model-bakery

### Changes

- **`requirements-dev.txt`**: `model-mommy==2.0.0` replaced with `model-bakery==1.3.3`
- **4 test files updated**:
  - `bireme/biblioref/tests.py` — import + 5 `mommy.make` calls → `baker.make`
  - `bireme/main/tests.py` — import + 1 `mommy.make` call → `baker.make`
  - `bireme/multimedia/tests.py` — import + 4 `mommy.make` calls → `baker.make`
  - `bireme/leisref/tests.py` — import + 5 `mommy.make` calls → `baker.make`

### Notes

- `model-bakery==1.3.3` is the last version supporting Python 3.7 and Django 2.2
- The API is a drop-in replacement: `mommy.make(...)` → `baker.make(...)`
- No `mommy.prepare()` calls were found in the codebase
