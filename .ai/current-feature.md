# Current Feature: Conditional Robots noindex for Staging

## Status

Completed

## Goals

- nginx sends `X-Robots-Tag: noindex, nofollow` only when `BLOCK_ROBOTS=true` (exact value); unset/empty/`false` sends no header, so prod `.env` needs no change
- `BLOCK_ROBOTS` is independent of `USE_AUTHENTICATION` and lives in the root `.env` (compose interpolation)
- Same conditional mechanism as basic auth (spec 008): new `conf/nginx/templates/robots.conf.template` with `map "${BLOCK_ROBOTS}" $robots_tag { default ""; true "noindex, nofollow"; }`, rendered to `/etc/nginx/robots.conf` by the nginx image's envsubst
- `www-static` (`conf/nginx/app/app.conf`) and `www-docs` (`conf/nginx/docs/docs.conf`) both `include /etc/nginx/robots.conf;` and set `add_header X-Robots-Tag $robots_tag always;` at server level — covering every path (incl. `/static/`, `/api/` redirect, uploaded PDFs) and error responses
- `docker-compose.yml`: `BLOCK_ROBOTS=${BLOCK_ROBOTS:-}` on both services; `www-docs` mounts only `robots.conf.template` (not the auth template) and sets `NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx`
- No `robots.txt`, no HTML meta tags; API stack untouched; existing security headers unchanged
- Verified locally with throwaway `nginx:1.30-alpine` containers (header present on all paths when on, absent when off, `nginx -t` OK, independent of auth); `docker compose config -q` OK; `make dev_test` green
- `.env-TEMPLATE` and README updated; log written in `.ai/logs/`; staging curl check after deploy

## Notes

- Spec: [009-conditional-robots-noindex-staging.md](.ai/features/009-conditional-robots-noindex-staging.md)
- Builds on spec 008 / PR #1587 — branch from `feature/conditional-http-basic-auth-for-staging`; PR targets it (or `main` once #1587 is merged)
- nginx omits `add_header` when the value is empty → `default ""` means no header when off
- `add_header` inheritance: server-level headers apply only to locations without their own `add_header`; currently no location in `app.conf`/`docs.conf` defines any — keep it that way (or repeat the header)
- Separate template file because `www-docs` doesn't define `USE_AUTHENTICATION`: envsubst would leave `${USE_AUTHENTICATION}` literal and nginx would fail on the unknown variable
- No `robots.txt`: `Disallow: /` prevents crawlers from seeing `noindex`, so known URLs could stay indexed
- Use Makefile targets for all build/test/manage commands (CLAUDE.md)
- Result 2026-11-11: implemented; verified locally (6 auth×robots combinations on app, on/off on docs, header on 200/302/401/404/502, security headers kept); `docker compose config -q` OK; `make dev_test` green (253 tests, 5 skipped); pending: staging curl check after deploy
- Log: [2026-11-11-conditional-robots-noindex-staging.md](.ai/logs/2026-11-11-conditional-robots-noindex-staging.md)

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
- 2026-11-11: "Conditional HTTP Basic Auth for Staging" implemented; commit `12cb3c48`, PR #1587 opened (pending merge and staging curl check); log [2026-11-11-conditional-basic-auth-staging.md](.ai/logs/2026-11-11-conditional-basic-auth-staging.md)
- 2026-11-11: Loaded "Conditional Robots noindex for Staging" — following spec [009-conditional-robots-noindex-staging.md](.ai/features/009-conditional-robots-noindex-staging.md)
- 2026-11-11: Starting "Conditional Robots noindex for Staging" on `feature/conditional-robots-noindex-for-staging` (from `feature/conditional-http-basic-auth-for-staging`) — following spec [009-conditional-robots-noindex-staging.md](.ai/features/009-conditional-robots-noindex-staging.md)
- 2026-11-11: Completed "Conditional HTTP Basic Auth for Staging" — squash-merged to `main` (PR #1587); commit `8903aad8`
