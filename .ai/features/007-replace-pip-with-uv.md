# Feature 007 — Replace pip with uv as package manager

**Date:** 2026-10-06
**Status:** Implemented (2026-10-07)

## Summary

Replace `pip` + `requirements*.txt` with **uv** (`pyproject.toml` + `uv.lock`) for installing
Python dependencies in the Docker images, and run every Python command through `uv run`.
uv defaults are kept: the environment is the project's `.venv` (no `UV_PROJECT_ENVIRONMENT`).

## Current state

- `Dockerfile` (base stage): `pip install --upgrade pip "setuptools<81"` then
  `pip install --no-cache-dir -r requirements.txt`; build deps (`gcc`, `musl-dev`, `libxml2-dev`,
  `libxslt-dev`, `python3-dev`, `pkgconf`) are removed after install; `mariadb-dev` stays.
- `Dockerfile` (dev stage): `pip install -r requirements-dev.txt`.
- Image: `python:3.14-alpine` (musl) → `mysqlclient` / `lxml` compiled in the image.
- Deps: `requirements.txt` (21 exact pins) and `requirements-dev.txt` (4 exact pins) at repo root.
- `setuptools<81` is required at runtime: `deform` 3.0.1, `src/utils/views.py` and `src/oer/views.py`
  import `pkg_resources`.
- `docker-compose-dev.yml` bind-mounts `./src/:/app/` (WORKDIR `/app`).
- `fabric/fabfile.py` `requirements` task: `pip install -r requirements.txt` in a server virtualenv.

## Decisions

| # | Topic | Decision |
|---|-------|----------|
| 1 | Dependency source | `pyproject.toml` + `uv.lock`; `requirements.txt` and `requirements-dev.txt` are **deleted** |
| 2 | Environment location | uv default: `.venv` next to `pyproject.toml` — no `UV_PROJECT_ENVIRONMENT` override |
| 3 | Project location | `src/pyproject.toml` + `src/uv.lock` → project root is `/app` in the container, venv is `/app/.venv` |
| 4 | Dev venv | Lives on the host as `src/.venv` (visible via the `./src/:/app/` mount), **created inside the dev container** (musl binaries — never run `uv sync` on the Arch host) |
| 5 | Running commands | `uv run` everywhere (compose, Makefile, scripts, crontab) — no `PATH` change |
| 6 | Sync policy | Dev: `uv run --frozen` (auto-syncs `.venv` from the lock before running) + `make dev_sync`. Prod: `.venv` baked at build with `uv sync --frozen --no-dev`, runtime uses `uv run --no-sync` |
| 7 | Version style | Compatible-release ranges on the audited versions (`~=X.Y.Z`, e.g. `Django~=5.2.18` = `>=5.2.18,<5.3`; changed 2026-10-07 from exact pins), exact versions fixed by `uv.lock`; `setuptools<81` becomes a declared dependency; dev deps go in `[dependency-groups] dev` |
| 8 | fabfile | `requirements` task switches to `uv sync --frozen --no-dev` in `src/` (untested — needs servers) |
| 9 | uv binary | `COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/` (`/bin` is on crond's PATH) |

## Goals / Acceptance criteria

### pyproject.toml / lock
- [x] `src/pyproject.toml` with `[project]` (name `fi-admin`, `requires-python = "==3.14.*"`), runtime
      `dependencies` = current `requirements.txt` pins + `"setuptools<81"`, and
      `[dependency-groups] dev` = current `requirements-dev.txt` pins; not a package
      (`[tool.uv] package = false`)
- [x] `src/uv.lock` generated and committed; resolved top-level versions identical to the old pins
- [x] `requirements.txt` and `requirements-dev.txt` removed

### Dockerfile
- [x] No `pip` invocation left; uv copied from `ghcr.io/astral-sh/uv:latest` (decision 9)
- [x] Base stage keeps `mariadb-dev` (runtime); `.build-deps` handling adapted per stage:
  - **prod**: copies `pyproject.toml`/`uv.lock`, runs `uv sync --frozen --no-dev --no-install-project`
    (BuildKit cache mount for `/root/.cache/uv`), then removes build deps; `COPY ./src/` must not
    bring a host `.venv`
  - **dev**: keeps the build deps installed (runtime `uv sync` compiles `mysqlclient`/`lxml`); no
    venv baked (it would be hidden by the bind mount)
- [x] `.venv` in prod readable by `appuser`; `uv run --no-sync` works as `appuser` (check uv cache/home dir)

### Ignore files
- [x] `.gitignore`: `src/.venv/`
- [x] New `.dockerignore`: excludes at least `src/.venv`, `.git`, `.ai`, `backups` (keep build context lean)

### uv run everywhere
- [x] `docker-compose-dev.yml`: `uv run --frozen python manage.py runserver 0.0.0.0:8000`
- [x] `docker-compose.yml`, `docker-compose-api.yml`: `uv run --no-sync gunicorn …` (crond command unchanged)
- [x] Makefile: every `python manage.py …` / test / coverage target uses `uv run` (`--frozen` for `dev_*`,
      `--no-sync` for `api_*`/`prod_*`)
- [x] `src/run_tests.sh`, `src/run_coverage.sh`: `uv run` for `python` / `coverage` (flag chosen to work in both dev and prod — `--no-sync` after the dev venv exists, or invoked via `uv run`)
- [x] `conf/crontab/{daily,weekly,monthly}/update_search_index`: `uv run --no-sync python manage.py …`
- [x] `proc/import/import2FIAdmin.sh`: `uv run --project /app --no-sync python /app/manage.py loaddata …`
- [x] `fabric/fabfile.py` `requirements` task: `uv sync --frozen --no-dev --active` in `src/` (untested on servers)

### Makefile targets (new)
- [x] `dev_sync`: `uv sync --frozen` in the dev container
- [x] `dev_lock`: `uv lock` in the dev container (regenerates `src/uv.lock` after editing `pyproject.toml`)

### Verification
- [ ] `make dev_build` + `make dev_up` creates `src/.venv` ✅ and runserver starts (pending: dev DB unreachable on 2026-10-07)
- [x] `make dev_test` green — same counts as baseline (249 tests, 5 skipped); `make dev_test_coverage` ≈ 60%
- [ ] `make dev_check` clean — pending: dev DB unreachable on 2026-10-07; `uv pip list` ✅ same versions as the pip build
- [x] `make prod_build` / `make api_build` succeed; prod container starts gunicorn as `appuser`; `exec` of a
      crontab script works (`uv run --no-sync` resolves from `/app`)
- [x] Prod image contains no `src/.venv` from the host and no `pip`-installed site-packages for the app
- [x] Image size / build time compared to the pip build (recorded in the log)
- [x] Log in `.ai/logs/2026-10-06-replace-pip-with-uv.md`

## Notes / Risks

- **musl vs glibc**: `src/.venv` must only be created by the container. Running `uv sync` on the Arch host
  would produce glibc wheels and a host-python symlink unusable in Alpine. Document this in README/AGENTS.
- **Dropbox**: the repo lives under Dropbox; `src/.venv` (thousands of files) will be synced unless ignored
  (e.g. `attr -s com.dropbox.ignored -V 1 src/.venv`). Record as a user action.
- **File ownership**: the dev container runs as root → `src/.venv` on the host is root-owned. Deleting it
  needs `sudo` or `make dev_exec cmd="rm -rf .venv"`.
- **`uv run --frozen` in dev** may compile `mysqlclient`/`lxml` on first start (slow first `dev_up`).
- **`uv run` as `appuser`** in prod: uv may need a writable cache dir even with `--no-sync`; if so set
  `UV_CACHE_DIR` to a writable path or `UV_NO_CACHE=1` for runtime (only if required).
- `PYTHON_VERSION` build arg must stay compatible with `requires-python`.
- `setuptools<81` must remain until `deform` / `pkg_resources` usages are replaced (out of scope).

## Out of scope

- Switching the base image (Alpine → Debian slim)
- Replacing `pkg_resources` usages / upgrading `deform`
- Running the fabfile against real servers (recorded as pending)
- Dependency version upgrades
