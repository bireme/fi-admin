# Replace pip with uv as package manager

**Date:** 2026-10-07 (spec/plan from 2026-10-06)
**Branch:** `feature/replace-pip-with-uv-as-package-manager`
**Spec:** [007-replace-pip-with-uv.md](../features/007-replace-pip-with-uv.md) · **Plan:** [022-replace-pip-with-uv.md](../plans/022-replace-pip-with-uv.md)

## Changes

- **`src/pyproject.toml`** (new): the 21 runtime deps from `requirements.txt` plus `"setuptools<81"`. The 4 dev deps are in `[dependency-groups] dev`. Each dep accepts newer patch releases of its current version, never older ones (`~=X.Y.Z`, e.g. `Django~=5.2.18` = `>=5.2.18,<5.3`; `colander~=2.0.0` keeps it on 2.0.x); `uv.lock` fixes the exact versions. Also sets `requires-python = "==3.14.*"` and `[tool.uv] package = false`.
- **`src/.python-version`** (new): `3.14`.
- **`src/uv.lock`** (new): 46 packages, generated with `make dev_lock` using the image's CPython 3.14.8.
- **`requirements.txt`, `requirements-dev.txt`**: deleted.
- **`Dockerfile`**: no pip left.
  - base: copies uv from `ghcr.io/astral-sh/uv:latest` and installs `mariadb-dev`.
  - dev: sets `UV_FROZEN=1` and `UV_LINK_MODE=copy` (the cache and the bind-mounted venv are on different filesystems), and keeps the build deps installed.
  - prod: sets `UV_NO_SYNC=1` and runs `uv sync --frozen --no-dev --no-install-project` with a BuildKit cache mount, then `apk del .build-deps`.
- **`.gitignore`**: adds `src/.venv/`.
- **`.dockerignore`** (new): `.git`, `.ai`, `backups`, `docs`, `src/.venv`, `src/htmlcov`, `**/__pycache__`, `.coverage`.
- **`uv run` everywhere**:
  - compose: runserver and gunicorn (×2).
  - Makefile: all `python manage.py` targets.
  - `src/run_tests.sh`, `src/run_coverage.sh`.
  - `conf/crontab/{daily,weekly,monthly}/update_search_index`.
  - `proc/import/import2FIAdmin.sh`.
- **Makefile**: new targets.
  - `dev_lock`: `run --rm --no-deps … env -u UV_FROZEN uv lock`. `UV_FROZEN=1` blocks `uv lock` ("Unable to find lockfile … UV_FROZEN=1"), so the target unsets it.
  - `dev_lock_upgrade`: `uv lock --upgrade`, or `--upgrade-package $(package)` when `package=` is given.
  - `dev_sync`: `uv sync`.
- **`fabric/fabfile.py`**: `requirements` now runs `uv sync --frozen --no-dev --active` in `env.root_path` with the server virtualenv active.
- **`README.md`**: new "Dependencies (uv)" section covering the lock/sync workflow, the rule that the venv is built only by the container, root ownership, and the Dropbox ignore.

## Version ranges (2026-10-07)

The exact `==X.Y.Z` pins became `~=X.Y.Z` compatible-release ranges (first tried `==X.Y.*`, switched to `~=` so versions can't go below the audited ones). Running `make dev_lock` afterwards left every resolved version unchanged (only the specifier metadata in `uv.lock` changed), and `make dev_sync` reports the env is in sync. To pick up new patch releases: `make dev_lock_upgrade` (all packages) or `make dev_lock_upgrade package=<name>`. The target unsets `UV_FROZEN`, which blocks `uv lock`, then run the tests.

## Verification

| Check | Result |
|-------|--------|
| `make dev_up` creates `src/.venv` | ✅ `.venv/bin/python` → `/usr/local/bin/python3.14` (no managed Python download) |
| `make dev_test` | ✅ 249 tests, 5 skipped, all OK |
| `make dev_test_coverage` | ✅ 60% (TOTAL 18850 / 7549 missed) |
| `uv pip list` vs baseline `pip freeze` | ✅ All 40 runtime packages identical (only `zope.deprecation` → `zope-deprecation` name normalization); +4 dev deps |
| `make prod_build_no_cache` | ✅ **36s** (pip baseline: **1m21s**) |
| Prod image size | 481MB (pip baseline: 469MB, +12MB from the uv/uvx binaries; uv does not precompile `.pyc`) |
| Prod imports (`MySQLdb`, `lxml.etree`, `pkg_resources`, `django`) as appuser | ✅ Django 5.2.18 |
| `whoami` in prod | ✅ `appuser`, no writable-cache problem with `UV_NO_SYNC=1` |
| Prod venv | ✅ `/app/.venv` root-owned, readable; python → `/usr/local/bin/python3`; no host venv leaked; pip has no app packages |
| gunicorn | ✅ starts and boots a worker as appuser; `--check-config` OK (with a cleaned env file and `DEBUG_TOOLBAR=0`) |
| Crontab scripts | ✅ `sh -n` OK; as root, `cd /app && uv run python manage.py help update_index` works |
| `make api_build` | ✅ |
| grep `pip install` / `requirements` | ✅ only the fabfile task name `requirements()` remains |

## Pending

- `make dev_check` / runserver: the dev DB `172.17.1.20` was unreachable from the host ("No route to host", probably VPN). Re-run when it is reachable.
- fabfile `requirements`: untested. The servers need uv installed.
- Browser smoke test and `rebuild_index` carried over from Phase 5.4–5.6.
- Dropbox ignore for `src/.venv` (user action): `attr -s com.dropbox.ignored -V 1 src/.venv`.

## Notes

- `docker run --env-file conf/app-env-dev` keeps inline `# comments` in values (e.g. `BRUTE_FORCE_THRESHOLD`), while compose strips them. This only affects ad-hoc `docker run` checks.
- `make dev_lock` writes `src/uv.lock` as root (the container runs as root). After locking, fix ownership with `make dev_exec cmd="chown $(id -u):$(id -g) uv.lock"`.
- The pip baseline image is kept locally as `bireme/fi-admin:baseline-pip` for comparison.
