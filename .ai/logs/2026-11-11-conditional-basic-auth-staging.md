# 2026-11-11 — Conditional HTTP Basic Auth for Staging

Spec: [008-conditional-basic-auth-staging.md](../features/008-conditional-basic-auth-staging.md)
Branch: `feature/conditional-http-basic-auth-for-staging`

## Summary

The `www-static` nginx (`docker-compose.yml`) now requires HTTP Basic Auth on the Django app (`location /`) when `USE_AUTHENTICATION=true` is set in the root `.env`. This keeps the staging environment private. It uses the same mechanism as iahx-opac (commit `747764d`): an nginx template maps the env var to `$auth_enable` (`"off"` or `"Restrict Access"`). Any value other than `true` leaves auth off, so production needs no change.

## Changes

- `conf/nginx/templates/variables.conf.template` (new): `map "${USE_AUTHENTICATION}" $auth_enable { default "off"; true "Restrict Access"; }`.
- `conf/nginx/app/app.conf`: `include /etc/nginx/variables.conf;` at http level, and `auth_basic $auth_enable;` plus `auth_basic_user_file /etc/nginx/.htpasswd;` in `location /`. `/static/` and the `/api/` redirect are unchanged and stay public.
- `docker-compose.yml` (`www-static`):
  - mounts `conf/nginx/templates` and `conf/nginx/.htpasswd`, both read-only;
  - sets env `USE_AUTHENTICATION=${USE_AUTHENTICATION:-}` and `NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx`.
- `Makefile`: new target `make htpasswd user=<name>`.
  - It prompts twice for the password with echo off and builds a bcrypt entry with `httpd:2.4-alpine htpasswd -niB`. The password goes in on stdin and never appears in argv.
  - It replaces any existing line for that user.
  - It refuses to run if `conf/nginx/.htpasswd` is a directory that Docker created.
  - `HTPASSWD_FILE` can be overridden.
- `.gitignore`: `.htpasswd`.
- `.env-TEMPLATE`: `USE_AUTHENTICATION=` with comments.
- `README.md`: new section "Staging access protection (HTTP basic auth)".

## Deviation from spec

The spec rendered the template into `/etc/nginx/vars`. The nginx image's `20-envsubst-on-templates.sh` skips rendering when the output dir is not writable, and a dir that doesn't exist counts as not writable. `$auth_enable` would then be undefined and nginx would fail to start. The rendered file now goes to `/etc/nginx`, which exists and is writable, and `app.conf` includes it explicitly as `/etc/nginx/variables.conf`. The bind-mounted `conf/nginx/app/` on the host still receives nothing.

## Verification

- Local test with a throwaway `nginx:1.30-alpine` container and the same mounts and env as `www-static`. `fi_admin` was pointed at localhost, so the `502` responses mean the request reached the proxy:
  - `true`: `nginx -t` passes. `/` without credentials returns `401` with `WWW-Authenticate: Basic realm="Restrict Access"`. Wrong credentials return `401`. Valid credentials return `502`, meaning the request was proxied. `/static/x.css` returns `404` and `/api/x` returns `302`, so neither asks for credentials.
  - `false` and empty: no auth on any path.
  - Auth off with `.htpasswd` missing: nginx starts and serves normally. Docker creates an empty root-owned directory at the mount path.
- `make htpasswd`, run under a pseudo-tty:
  - adds users and replaces an existing user's entry;
  - `htpasswd -vb` confirms the stored passwords;
  - rejects mismatched passwords and a missing `user=`.
- `docker compose config -q` passes. The variable renders as `"true"` when set and `""` when unset.
- `make dev_test`: all green (253 tests, 5 skipped).

## Pending

- Staging: set `USE_AUTHENTICATION=true` in `.env`, run `make htpasswd user=<name>` and then `make prod_up`. Check with `curl -I`: `401` without credentials, `200`/`302` with them, and `200` for `/static/css/screen.css` without them.
- Production: run `touch conf/nginx/.htpasswd` before the next `make prod_up`. This step is optional.
