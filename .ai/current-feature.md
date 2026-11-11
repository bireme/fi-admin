# Current Feature: Conditional HTTP Basic Auth for Staging

## Status

In Progress

## Goals

- nginx `www-static` (`docker-compose.yml`, `conf/nginx/app/app.conf`) enforces HTTP Basic Auth on `location /` only when `USE_AUTHENTICATION=true`; any other value (unset/empty/false) leaves it off, so prod `.env` needs no change
- Same mechanism as iahx-opac (commit `747764d`): `conf/nginx/templates/variables.conf.template` with `map "${USE_AUTHENTICATION}" $auth_enable { default "off"; true "Restrict Access"; }`, rendered by the nginx image's envsubst
- `/static/` and the `/api/` redirect stay public; `www-docs` and the API stack are untouched
- Credentials in gitignored `conf/nginx/.htpasswd`, mounted read-only at `/etc/nginx/.htpasswd`; `make htpasswd user=<name>` creates/appends a bcrypt entry via `httpd:2.4-alpine` with an interactive password prompt
- Rendered `variables.conf` goes to `/etc/nginx` (`NGINX_ENVSUBST_OUTPUT_DIR`), included as `/etc/nginx/variables.conf` from the top of `app.conf` — nothing written into the bind-mounted `conf/nginx/app/` on the host
- `.gitignore`, `.env-TEMPLATE` and README document `USE_AUTHENTICATION`, `make htpasswd` and `touch conf/nginx/.htpasswd` for hosts without auth
- Manual staging check: `401` + `WWW-Authenticate: Basic realm="Restrict Access"` without creds; `200`/`302` with creds; `/static/css/screen.css` `200` without creds; no change when the var is unset
- `make dev_test` stays green; log written in `.ai/logs/`

## Notes

- Spec: [008-conditional-basic-auth-staging.md](.ai/features/008-conditional-basic-auth-staging.md)
- Reference: iahx-opac `docker/nginx/templates/variables.conf.template`, `docker/nginx/nginx.conf:285-287`, `docker-compose.yml` webserver service
- API stack excluded: tastypie `ApiKeyAuthentication` (`src/api/oer_api.py:34`) may use the `Authorization` header, and its nginx is 1.18 (no templates support)
- `USE_AUTHENTICATION` lives in the root `.env` (compose interpolation), not `conf/app-env`
- If `conf/nginx/.htpasswd` is missing, Docker creates an empty dir at the mount path — harmless while auth is off
- Verification is manual on staging (no nginx-check Makefile target, per spec decision 5)
- Use Makefile targets for all build/test/manage commands (CLAUDE.md)
- Decision 2026-11-11 (start): output dir changed from the spec's `/etc/nginx/vars` to `/etc/nginx` — the nginx entrypoint skips rendering when the output dir doesn't exist (`[ ! -w "$output_dir" ]`), which would leave `$auth_enable` undefined and break nginx startup
- Result 2026-11-11: implemented; verified locally with throwaway `nginx:1.30-alpine` (401 + realm without/bad creds, pass-through with creds, `/static/` and `/api/` public, off for `false`/empty, missing `.htpasswd` OK when off); `make htpasswd` tested; `make dev_test` green (253 tests, 5 skipped); pending: staging curl check after deploy
- Log: [2026-11-11-conditional-basic-auth-staging.md](.ai/logs/2026-11-11-conditional-basic-auth-staging.md)

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
- 2026-10-07: Completed "Replace pip with uv as package manager" — merged to `main` (PR #1584); commit `ab7f7bb5`
- 2026-10-28: Loaded "Cache-busting version parameter for screen.css" — inline description
- 2026-10-28: Starting "Cache-busting version parameter for screen.css" on `feature/cache-busting-version-parameter-for-screen-css` (from `feature/sidebar-menu-and-dashboard-polish`) — following plan [023-versioned-static-screen-css.md](.ai/plans/023-versioned-static-screen-css.md)
- 2026-11-11: Completed "Cache-busting version parameter for screen.css" — `{% versioned_static %}` tag on `main`; log [2026-10-28-versioned-static-screen-css.md](.ai/logs/2026-10-28-versioned-static-screen-css.md)
- 2026-11-11: Loaded "Conditional HTTP Basic Auth for Staging" — following spec [008-conditional-basic-auth-staging.md](.ai/features/008-conditional-basic-auth-staging.md)
- 2026-11-11: Starting "Conditional HTTP Basic Auth for Staging" on `feature/conditional-http-basic-auth-for-staging` — following spec [008-conditional-basic-auth-staging.md](.ai/features/008-conditional-basic-auth-staging.md)
