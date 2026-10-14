# Plan 019 — Fix nginx API webserver file descriptor exhaustion (nginx layer only)

## Context

`fi-admin-api-webserver` (`nginx:1.18-alpine` in `docker-compose-api.yml`) logs
`[crit] 24#24: accept4() failed (24: No file descriptors available)`.

Errno 24 is EMFILE: an nginx worker has hit its open-file limit. Each proxied request holds about 2 fds, one for the client and one for the gunicorn unix socket. Gunicorn runs only 2 sync workers, so requests queue in nginx. Today nginx holds each of them for up to 600s. `proxy_ignore_client_abort on` keeps the upstream side open even after the client has gone. Meanwhile the worker runs with the image defaults (`worker_connections 1024`, and the container's nofile limit).

**Scope (user decision):** only the nginx layer changes. That covers the API webserver's nginx config and its service definition in compose. Gunicorn workers and timeouts stay as they are. Decisions made:
- `proxy_read_timeout` 300s and `proxy_connect_timeout` 10s
- remove `proxy_ignore_client_abort`
- bump the image to `nginx:1.30-alpine`

Dropped from the loaded goals: upstream keepalive. Gunicorn sync workers close the connection after every response, so `keepalive` in the upstream block would do nothing. The gunicorn-capacity goal moves to a possible follow-up feature.

## Changes

### 1. New main config: `conf/nginx/nginx-base.conf`
This file can't live inside `conf/nginx/api/`. That directory is mounted as `conf.d`, and the `*.conf` glob would pull this file into `http {}`, where `events {}` isn't allowed. It is based on the official image's default `nginx.conf`, plus:
- `worker_processes auto;`
- `worker_rlimit_nofile 65535;` raises the per-worker fd limit
- `events { worker_connections 16384; }`. That is about 8k concurrent proxied requests at 2 fds each, well under the 65535 rlimit
- in `http {}`:
  - `keepalive_timeout 15s;` (default 65s), so idle client keep-alives free their fds sooner
  - `client_header_timeout 30s;` and `client_body_timeout 30s;` (default 60s)
  - `reset_timedout_connection on;`, which closes timed-out sockets immediately instead of leaving them in FIN_WAIT
- keep `include /etc/nginx/mime.types`, the `main` log format, `access_log`/`error_log` (stdout/stderr through the image symlinks), `sendfile on`, `server_tokens off`, and `include /etc/nginx/conf.d/*.conf;`

### 2. `conf/nginx/api/app.conf` (location `/`)
- remove `proxy_ignore_client_abort on;`
- `proxy_connect_timeout 10s;` (from 600). Connecting to a local unix socket is instant unless gunicorn's backlog is full, so fail fast in that case
- `proxy_read_timeout 300s;` (from 600)
- `proxy_send_timeout 60s;` and `send_timeout 60s;` (from 600). These are timeouts between two successive writes, not total transfer time, so 60s is plenty
- move `server_tokens off` to the main config (it can stay here too; harmless)
- leave the upstream, the headers, the cache headers and `/static/` unchanged

### 3. `docker-compose-api.yml`, `webserver` service
- `image: nginx:1.30-alpine`
- add the mount `./conf/nginx/nginx-base.conf:/etc/nginx/nginx.conf:ro`
- add:
  ```yaml
  ulimits:
    nofile:
      soft: 65535
      hard: 65535
  ```

### 4. `Makefile` (API section, following the existing `api_*` pattern)
- `api_webserver_test`: `docker compose -f $(COMPOSE_FILE_API) run --rm --no-deps webserver nginx -t`
- `api_webserver_limits`: prints `Max open files` from `/proc/<worker pid>/limits` inside the container (for checking prod)

### 5. Docs and bookkeeping
- Copy this plan to `.ai/plans/019-fix-nginx-api-fd-exhaustion.md`, and link it in `## Detailed Plan` of `.ai/current-feature.md`. Update the Goals there to the nginx-only scope (drop keepalive and gunicorn)
- Write the log `.ai/logs/2026-10-14-fix-nginx-api-fd-exhaustion.md`, with deploy steps (`git pull && make api_webserver_test && make api_up`; compose recreates the webserver because its config changed) and a note to also check the external `nginx-proxy` container for the same error

## Verification
1. `make api_webserver_test` prints `syntax is ok` / `test is successful` with nginx 1.30
2. `make api_up`, then `make api_webserver_limits` shows `Max open files 65535` for the worker processes
3. `docker compose -f docker-compose-api.yml exec webserver nginx -T | grep -E 'worker_(rlimit|connections)|proxy_.*timeout|ignore_client'` shows the new values, and no `proxy_ignore_client_abort`
4. Smoke test through the webserver, e.g. `curl -sI http://<webserver>/api/...` and `/static/...`, both return 200 (run it from a container on the `nginx-proxy` network, or with `docker compose exec webserver wget -qO- localhost/...`)
5. Optional stress check: open about 3000 concurrent idle connections against the webserver (a small Python socket script, kept in the scratchpad) and confirm there is no `accept4() failed` in `make api_logs`

## Addendum (2026-10-14) — shared base config

At the user's request, `conf/nginx/nginx-api.conf` was renamed to `conf/nginx/nginx-base.conf` and is now also used by `docker-compose.yml`:
- `www-static` and `www-docs`: mount `./conf/nginx/nginx-base.conf:/etc/nginx/nginx.conf:ro` and set `ulimits.nofile` 65535. The ulimit is required, because without `CAP_SYS_RESOURCE` nginx cannot raise `worker_rlimit_nofile` above the container's hard limit
- New Makefile target `prod_webserver_test` runs `nginx -t` for both. `www-static`'s upstream `fi_admin:8000` is resolved at config load, so the target maps `fi_admin` to 127.0.0.1 in the throwaway container's `/etc/hosts`

