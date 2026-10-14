# 2026-10-14 — Fix nginx API webserver file descriptor exhaustion

Plan: [019-fix-nginx-api-fd-exhaustion.md](../plans/019-fix-nginx-api-fd-exhaustion.md)
Branch: `feature/fix-nginx-api-webserver-file-descriptor-exhaustion`

## Problem

`fi-admin-api-webserver` logged `[crit] 24#24: accept4() failed (24: No file descriptors available)`.
An nginx worker had hit its open-file limit (EMFILE). Gunicorn runs only 2 sync workers, so requests queue in nginx, which held each one for up to 600s. `proxy_ignore_client_abort on` also kept the upstream fd open after the client was gone. nginx ran with the image defaults (`worker_connections 1024`, container nofile limit).

Scope: only the nginx layer changes. Gunicorn is unchanged.

## Changes

- **`conf/nginx/nginx-base.conf`** (new): shared main nginx config, mounted at `/etc/nginx/nginx.conf` by the API webserver and by `www-static`/`www-docs` in `docker-compose.yml`. It was first named `nginx-api.conf`, then renamed when it was reused for the regular compose file. It is based on the `nginx:1.30-alpine` default and adds:
  - `worker_rlimit_nofile 65535` and `worker_connections 16384`
  - `keepalive_timeout 15s`, `client_header_timeout 30s`, `client_body_timeout 30s`
  - `reset_timedout_connection on` and `server_tokens off`

  It lives outside `conf/nginx/{api,app,docs}/`, because those directories are mounted as `conf.d` and included inside `http {}`.
- **`conf/nginx/api/app.conf`**: removed `proxy_ignore_client_abort on`. Timeouts are now:
  - `proxy_connect_timeout 10s`
  - `proxy_read_timeout 300s`
  - `proxy_send_timeout 60s` and `send_timeout 60s`

  All of them were 600 before.
- **`docker-compose-api.yml`** (`webserver`): image `nginx:1.18-alpine` → `nginx:1.30-alpine`, `ulimits.nofile` 65535/65535, and the new `nginx.conf` mounted read-only.
- **`docker-compose.yml`** (`www-static`, `www-docs`): mount `nginx-base.conf` read-only and set `ulimits.nofile` 65535/65535. The ulimit is required, because nginx cannot raise `worker_rlimit_nofile` above the container's hard limit.
- **`Makefile`**:
  - `api_webserver_test` runs `nginx -t` in a throwaway webserver container
  - `api_webserver_limits` prints `Max open files` for every nginx process
  - `prod_webserver_test` runs `nginx -t` for `www-static` and `www-docs`. `www-static` resolves `fi_admin:8000` at load, so the target maps `fi_admin` to 127.0.0.1 inside the throwaway container

## Verification (local)

- `make api_webserver_test` and `make prod_webserver_test`: syntax ok, test successful (nginx 1.30) for all three webservers.
- `make api_webserver_limits`: master and all workers show `Max open files 65535`.
- `nginx -T` shows the new values, and `proxy_ignore_client_abort` is gone.
- Stress test with 3000 concurrent idle connections (an incomplete-request script in the scratchpad):
  - **old** setup (`nginx:1.18-alpine` + old `app.conf`, nofile 1024): reproduced `accept4() failed (24: No file descriptors available)` 14 times
  - **new** setup: all 3000 accepted, nginx still served a probe request, and no fd errors in the logs

## Deploy

```sh
git pull
make api_webserver_test
make api_up          # compose recreates the webserver (image, ulimits and mount changed)
make api_webserver_limits

# regular stack
make prod_webserver_test
make prod_up         # recreates www-static and www-docs (ulimits and mount changed)
```

Note: `nginx-base.conf` is a single-file bind mount. `git pull` replaces the file with a new inode, so a running container keeps reading the old one. After future edits to this file, recreate the webservers (`docker compose ... up -d --force-recreate <service>`). `nginx -s reload` is not enough.

## Follow-ups

- There's an existing bug in the `Makefile`: `prod_exec_webserver` runs `exec webserver`, but `docker-compose.yml` has no `webserver` service (the webservers are `www-static` and `www-docs`).

- The root cause is still in place: gunicorn handles only 2 requests at a time (`--workers 2 --timeout 1000`). Consider more workers or threads, and a lower timeout, in a separate feature.
- Check whether the external `nginx-proxy` container logs the same error. It is not managed by this repo.
- API calls that take longer than 300s now get a 504 from nginx.
