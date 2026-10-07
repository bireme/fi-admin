# Plan 022 — Replace pip with uv as package manager

Implements spec [007-replace-pip-with-uv.md](.ai/features/007-replace-pip-with-uv.md).

## Context

Today the Docker images install their dependencies with `pip` from two pinned files at the repo root (`requirements.txt` and `requirements-dev.txt`). That gives no lock for transitive deps, and pip is slow to install. The goal is to move to uv (`pyproject.toml` + `uv.lock`) while keeping uv's defaults: the venv is `.venv` next to `pyproject.toml`, and every command runs through `uv run`.

The dev compose mounts `./src/:/app/`, so the project goes in `src/`. In dev, the venv lives on the host as `src/.venv` but is built inside the container. The image is Alpine (musl), so a venv built on the Arch host would not work.

Decisions from the spec plus this planning round:

- **Pins:** exact `==` pins are kept, `setuptools<81` becomes a declared dependency, and the dev deps go in a `dev` dependency group.
- **uv behavior per stage, via env vars:**
  - dev stage: `ENV UV_FROZEN=1`, so `uv run` syncs from the lock and never re-locks
  - prod stage: `ENV UV_NO_SYNC=1`, so it uses the `.venv` built into the image as is
  - every command is a plain `uv run …`
- **fabfile:** the `requirements` task uses `uv sync`, with no server test.

## Steps

### 0. Baseline (before any change)
- Build the current image with `make prod_build_no_cache`. Record the build time with `time`, the image size from `docker images`, and the output of `docker run --rm <tag> pip freeze`. Save these in the scratchpad.

### 1. `src/pyproject.toml` (new)
```toml
[project]
name = "fi-admin"
version = "0"            # version comes from APP_VERSION/git, not used
requires-python = "==3.14.*"   # matches Dockerfile PYTHON_VERSION=3.14
dependencies = [ <21 pins from requirements.txt>, "setuptools<81" ]

[dependency-groups]
dev = [ <4 pins from requirements-dev.txt> ]

[tool.uv]
package = false
```
Also add `src/.python-version` with `3.14` (uv's default pin file), so `uv lock`, `uv sync` and `uv run` pick Python 3.14. The Dockerfile `PYTHON_VERSION` ARG stays at `3.14`.

Delete `requirements.txt` and `requirements-dev.txt`.

### 2. Dockerfile
- **base:**
  - keep the ARG and ENV lines
  - add `COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/`
  - `apk add --no-cache mariadb-dev` (runtime)
  - keep `EXPOSE 8000` and `WORKDIR /app`
  - no pip
- **dev:**
  - `ENV UV_FROZEN=1`
  - `apk add --no-cache make gcc musl-dev libxml2-dev libxslt-dev python3-dev pkgconf`. These are permanent, because `mysqlclient` and `lxml` get compiled at runtime by `uv run`/`dev_sync` into `/app/.venv`, which is `src/.venv` on the host.
  - No venv is built into the dev image.
- **prod:**
  - `ENV UV_NO_SYNC=1`
  - `COPY ./src/pyproject.toml ./src/uv.lock /app/`
  - one `RUN --mount=type=cache,target=/root/.cache/uv` that does:
    - `apk add --virtual .build-deps …`
    - `UV_LINK_MODE=copy uv sync --frozen --no-dev --no-install-project`
    - `apk del .build-deps`
  - Then the existing crontab, appuser and `COPY ./src/` steps, unchanged. `.venv` is owned by root and is readable by appuser.
- Keep the `setuptools<81` comment, moved into pyproject.toml.

### 3. Ignore files
- `.gitignore`: add `src/.venv/`.
- New `.dockerignore`: `.git`, `.ai`, `backups`, `docs`, `src/.venv`, `src/htmlcov`, `**/__pycache__`, `.coverage`. This stops prod `COPY ./src/` from overwriting the built `.venv` with the host venv.

### 4. `uv run` everywhere (plain `uv run`, no flags)
- `docker-compose-dev.yml`: `command: uv run python manage.py runserver 0.0.0.0:8000`
- `docker-compose.yml`, `docker-compose-api.yml`: `uv run gunicorn …`. The cron `crond -f` command stays as is, because the scripts call `uv run` themselves.
- `Makefile`: every `python manage.py` / `python -W… manage.py` becomes `uv run python …`. This covers:
  - dev_makemigrations, _check, migrate, sqlmigrate, check, check_deploy, update_index
  - test_app, test_deprecations, update_translations, loaddata
  - api_exec_collectstatic, prod_exec_collectstatic, prod_loaddata, prod_migrate

  `dev_test`, `dev_test_coverage` and `prod_test` keep `sh run_*.sh`; the scripts do the `uv run`.
- `src/run_tests.sh`: `uv run python -W ignore manage.py test …`. `src/run_coverage.sh`: `uv run coverage run|report|html`.
- `conf/crontab/{daily,weekly,monthly}/update_search_index`: `uv run python manage.py …`. They already `cd /app`, and crond passes the container env, as the existing `$HAYSTACK_CONNECTION_URL` use shows.
- `proc/import/import2FIAdmin.sh`: `uv run python /app/manage.py loaddata …`. uv finds `/app/pyproject.toml` by walking up from `/app/proc/import`.

### 5. Makefile targets (new)
- `dev_lock`: `docker compose -f $(COMPOSE_FILE_DEV) run --rm --no-deps fi_admin uv lock`. It uses `run`, not `exec`, so it works before a lock exists, when the dev container can't start yet.
- `dev_sync`: `docker compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin uv sync`

### 6. fabfile
In `requirements()`, do `cd(env.root_path)` (where `manage.py` and `pyproject.toml` live), keep the virtualenv `prefix`, and run `uv sync --frozen --no-dev --active`. `--active` installs into the existing server virtualenv, so `migrate` and the other tasks don't change. Servers need uv installed; this is recorded as pending.

### 7. Docs
Add a short "Dependencies (uv)" section to README.md covering:
- edit `src/pyproject.toml`, then run `make dev_lock`
- `make dev_sync`
- `src/.venv` is built only by the container (musl), never by running `uv sync` on the host
- Dropbox ignore: `attr -s com.dropbox.ignored -V 1 src/.venv`
- `src/.venv` is owned by root

### 8. Lock + build
`make dev_lock`, which generates `src/uv.lock`, then `make dev_build`, `make dev_up` (the first start compiles the venv), then `make dev_logs` to confirm runserver is up.

### 9. Log + tracking
Write `.ai/logs/2026-10-06-replace-pip-with-uv.md` with the changes, the baseline vs uv numbers and the pending items. Tick the spec goals.

## Critical files
`Dockerfile`, `src/pyproject.toml` (new), `src/.python-version` (new), `src/uv.lock` (new), `.dockerignore` (new), `.gitignore`, `Makefile`, `docker-compose*.yml`, `src/run_tests.sh`, `src/run_coverage.sh`, `conf/crontab/*/update_search_index`, `proc/import/import2FIAdmin.sh`, `fabric/fabfile.py`, `README.md`

## Risks to check during implementation
- **`UV_FROZEN=1` with `uv lock`:** confirm it doesn't block `dev_lock`. If it does, unset it in that target with `env -u UV_FROZEN` or `-e UV_FROZEN=`.
- **`uv run` as appuser:** confirm it works with `UV_NO_SYNC=1` and doesn't need a writable `/app`. The cache goes to `~appuser/.cache`, and `adduser -S` creates the home dir. If it fails, set `UV_CACHE_DIR=/tmp/uv-cache` in prod only.
- **`.venv/bin/python` symlink:** check it points to `/usr/local/bin/python3.14` in both stages, so uv doesn't download a managed Python.
- **`apk del .build-deps` in prod:** it must leave the runtime libs (`mariadb-connector-c`, `libxml2`, `libxslt`). Same pattern as today; confirm by importing `MySQLdb` and `lxml.etree`.

## Verification
1. `make dev_test`: 249 tests, 5 skipped, green.
2. `make dev_test_coverage`: about 60%.
3. `make dev_check`.
4. `make dev_exec cmd="uv pip list --format freeze"`: compare with the baseline `pip freeze`. Top-level pins must be identical; differences in transitive deps are noted.
5. `make prod_build_no_cache` (timed):
   - image size vs baseline
   - `docker run --rm <tag> uv run python -c "import MySQLdb, lxml.etree, pkg_resources, django; print(django.get_version())"`
   - `docker run --rm <tag> whoami` → appuser
   - no `src/.venv` leaked from the host: built `.venv/bin/python` is a symlink to `/usr/local/bin`
6. `make api_build` succeeds.
7. Run gunicorn in a prod container (`docker run --rm --env-file conf/app-env-dev … uv run gunicorn --check-config fi-admin.wsgi`) and check the crontab script syntax (`sh -n`).
8. `grep -rn "pip install\|requirements" Dockerfile Makefile fabric conf src/*.sh` → nothing left.
