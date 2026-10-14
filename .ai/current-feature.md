# Current Feature: Fix nginx API webserver file descriptor exhaustion

## Status

In Progress

## Goals

- `fi-admin-api-webserver` no longer logs `[crit] accept4() failed (24: No file descriptors available)` under normal and peak API load
- Scope is the nginx layer only. Gunicorn workers and timeouts are unchanged
- New main config `conf/nginx/nginx-base.conf` (mounted at `/etc/nginx/nginx.conf`): `worker_rlimit_nofile 65535`, `worker_connections 16384`, shorter client keepalive and header/body timeouts, and `reset_timedout_connection on`
- `docker-compose-api.yml` webserver: `ulimits.nofile` 65535 and image `nginx:1.30-alpine`
- `conf/nginx/nginx-base.conf` is shared: `docker-compose.yml` `www-static` and `www-docs` also mount it, with the same `ulimits.nofile`
- `conf/nginx/api/app.conf`: `proxy_ignore_client_abort` removed, read timeout 300s, connect 10s, send and `send_timeout` 60s
- Makefile targets `api_webserver_test`, `prod_webserver_test` (`nginx -t`) and `api_webserver_limits` work
- A log is written in `.ai/logs/`

## Notes

- Error source: the `webserver` service (`fi-admin-api-webserver`, `nginx:1.18-alpine`) in `docker-compose-api.yml`. Only `conf/nginx/api/` is mounted at `/etc/nginx/conf.d`, which is included inside `http {}`. So `worker_rlimit_nofile` and `events { worker_connections }` cannot be set there. A full `nginx.conf` has to be mounted at `/etc/nginx/nginx.conf`
- Errno 24 is EMFILE, the per-process fd limit. Each proxied request uses about 2 fds (the client socket and the upstream socket). The image default is `worker_connections 1024`, and the container nofile soft limit may be as low as 1024
- Likely root cause is upstream saturation, not the fd limit itself. Gunicorn runs 2 sync workers (`.env` `GUNICORN_PARAMS=--workers 2 --timeout 1000`). Slow API calls hold the workers for a long time. Meanwhile nginx keeps client connections open for up to 600s, and `proxy_ignore_client_abort on` keeps upstream connections open even after the client leaves. Raising limits alone only delays the failure
- Out of scope (user decision): gunicorn tuning such as `--workers`/`--threads`/`--timeout`. Candidate for a follow-up feature
- Also check whether the external `nginx-proxy` container logs the same error, because that one is out of this repo's control
- Deploy: `make api_up`. Compose recreates the webserver because its config changed (ulimits, image, new mount)

## Detailed Plan

[019-fix-nginx-api-fd-exhaustion.md](.ai/plans/019-fix-nginx-api-fd-exhaustion.md)

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
- 2026-10-14: Completed "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — merged to `main` via PR #1578; commit `2b9f4542`
- 2026-10-14: Loaded "Fix nginx API webserver file descriptor exhaustion" — inline description
- 2026-10-14: Starting "Fix nginx API webserver file descriptor exhaustion" on `feature/fix-nginx-api-webserver-file-descriptor-exhaustion` — following plan [019-fix-nginx-api-fd-exhaustion.md](.ai/plans/019-fix-nginx-api-fd-exhaustion.md)
