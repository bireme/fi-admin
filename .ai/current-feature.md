# Current Feature: Replace pip with uv as package manager

## Status

In Progress

## Goals

- `src/pyproject.toml` + `src/uv.lock` replace `requirements.txt` / `requirements-dev.txt` (deleted): compatible-release ranges `~=X.Y.Z` on the current versions (exact versions in the lock; `make dev_lock_upgrade` to bump), `"setuptools<81"` declared (needed by `pkg_resources` in deform, `utils/views.py`, `oer/views.py`), dev deps in `[dependency-groups] dev`, `[tool.uv] package = false`, resolved top-level versions unchanged
- `Dockerfile` has no `pip`: uv copied from `ghcr.io/astral-sh/uv:latest`; Python pinned to 3.14 (`requires-python = "==3.14.*"` + `src/.python-version`)
  - prod: `uv sync --frozen --no-dev --no-install-project` bakes `/app/.venv` (BuildKit cache mount), build deps removed, readable/usable by `appuser`
  - dev: build deps kept (runtime compile of `mysqlclient`/`lxml`), no baked venv
- uv defaults kept: venv is `.venv` next to `pyproject.toml` (no `UV_PROJECT_ENVIRONMENT`); in dev it lives on the host as `src/.venv`, created only inside the container
- Plain `uv run` everywhere (dev image `UV_FROZEN=1` auto-syncs, prod image `UV_NO_SYNC=1`) — compose files (runserver/gunicorn), Makefile targets, `run_tests.sh`, `run_coverage.sh`, crontab `update_search_index` scripts, `proc/import/import2FIAdmin.sh`
- New Makefile targets `dev_sync` (`uv sync`) and `dev_lock` (`uv lock`) run in the dev container
- `.gitignore` gets `src/.venv/`; new `.dockerignore` (at least `src/.venv`, `.git`, `.ai`, `backups`)
- `fabric/fabfile.py` `requirements` task uses `uv sync --frozen --no-dev` in `src/` (untested, pending)
- Verified: `make dev_build`/`dev_up` creates `src/.venv` and runserver starts; `make dev_test` green (249 tests, 5 skipped), coverage ≈ 60%; `make dev_check` clean; `prod_build`/`api_build` succeed, gunicorn runs as `appuser`, crontab script runs; image size/build time compared with pip build
- Log written in `.ai/logs/2026-10-06-replace-pip-with-uv.md`

## Notes

- Spec: [007-replace-pip-with-uv.md](.ai/features/007-replace-pip-with-uv.md) (decisions table, acceptance criteria, risks)
- Never run `uv sync` on the Arch host: image is Alpine/musl, host venv would be glibc and unusable in the container
- `src/.venv` sits in Dropbox (exclude with `attr -s com.dropbox.ignored -V 1 src/.venv`) and is root-owned (remove via container or sudo)
- First `make dev_up` may be slow (compiles `mysqlclient`/`lxml`)
- If `uv run --no-sync` as `appuser` needs a writable cache, set `UV_CACHE_DIR`/`UV_NO_CACHE` for runtime only
- Out of scope: Alpine → Debian switch, replacing `pkg_resources`/upgrading `deform`, running the fabfile against servers, dependency upgrades
- Use Makefile targets for all build/test/manage commands (CLAUDE.md)
- Result 2026-10-07: implemented; 249 tests OK (5 skipped), coverage 60%; runtime versions identical to pip build; prod build 36s vs 1m21s (pip), image 481MB vs 469MB; gunicorn/cron/api_build OK; `dev_lock` needs `env -u UV_FROZEN`
- Pending: `make dev_check` + runserver start (dev DB 172.17.1.20 unreachable on 2026-10-07), fabfile on servers (needs uv), Dropbox ignore for `src/.venv`
- Log: [2026-10-06-replace-pip-with-uv.md](.ai/logs/2026-10-06-replace-pip-with-uv.md)
- Decision 2026-10-06 (plan): uv behavior set per Docker stage via env — dev `UV_FROZEN=1`, prod `UV_NO_SYNC=1` — so every command is a plain `uv run …`; fabfile uses `uv sync --frozen --no-dev --active` in the server virtualenv

## Detailed Plan

[022-replace-pip-with-uv.md](.ai/plans/022-replace-pip-with-uv.md)

## History

- 2026-04-13: Completed "Add indexed_database filter to LeisRef API" — filter legislation by database acronym via ?indexed_database param
- 2026-04-14: Completed "Add User-Agent header to EmailModelBackend" — hardcoded `fi-admin/2.3` UA in `src/biremelogin/authenticate.py` to avoid proxy blocks
- 2026-05-27: Starting "Django Upgrade Phase 2 — Deprecation Fixes" — following spec [003-upgrade-django-phase2-deprecation-fixes.md](.ai/features/003-upgrade-django-phase2-deprecation-fixes.md)
- 2026-07-17: Completed "Django Upgrade Phase 2 — Deprecation Fixes" — merged into `rc/3.2` flow; commit `4ee052a`
- 2026-07-17: Starting "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — following spec [004-upgrade-django-phase3-django-3.2.md](.ai/features/004-upgrade-django-phase3-django-3.2.md)
- 2026-08-27: Completed "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — merged to `main`; commit `c0ba51a`
- 2026-08-27: Starting "Django Upgrade Phase 4 — Django 3.2 → 4.2 LTS" — following plan [018-upgrade-django-phase4-django-4.2.md](.ai/plans/018-upgrade-django-phase4-django-4.2.md)
- 2026-09-28: Phase 4 "Django 3.2 → 4.2 LTS" implemented; commit `5d2e234a` is on `validation` (not yet merged to `main`)
- 2026-09-28: Loaded "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — following spec [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
- 2026-09-28: Starting "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" on `setup/django-5.2` — following spec [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
- 2026-10-06: Completed "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — merged to `main` (PR #1578); commit `cf369f75`
- 2026-10-06: Loaded "Django Upgrade Phase 5.1 — Keep jsonfield" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) task 5.1
- 2026-10-06: Starting "Django Upgrade Phase 5.1 — Keep jsonfield" — following plan [019-keep-jsonfield-django-5.2.md](.ai/plans/019-keep-jsonfield-django-5.2.md)
- 2026-10-06: Loaded "Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) tasks 5.2 and 5.3
- 2026-10-06: Starting "Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps" — following plan [020-upgrade-python-3.14-django-5.2-deps.md](.ai/plans/020-upgrade-python-3.14-django-5.2-deps.md)
- 2026-10-06: Phases 5.2 & 5.3 "Python 3.14 + Django 5.2 dependency bumps" implemented; commit `39b95b46` on `feature/django-upgrade-phase-5.2-5.3` (not yet merged)
- 2026-10-06: Loaded "Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) tasks 5.4–5.6
- 2026-10-06: Starting "Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations" — following plan [021-django-5.2-breaking-changes-tastypie-migrations.md](.ai/plans/021-django-5.2-breaking-changes-tastypie-migrations.md)
- 2026-10-06: Phases 5.4–5.6 "Django 5.x breaking changes, tastypie checks, migrations" implemented; commit `2f3d95a3` on `validation` (pending manual checks: `rebuild_index`, browser smoke)
- 2026-10-06: Loaded "Replace pip with uv as package manager" — following spec [007-replace-pip-with-uv.md](.ai/features/007-replace-pip-with-uv.md)
- 2026-10-07: Starting "Replace pip with uv as package manager" — following plan [022-replace-pip-with-uv.md](.ai/plans/022-replace-pip-with-uv.md)
