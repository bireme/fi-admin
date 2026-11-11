# 2026-11-11 — Conditional Robots noindex for Staging

Spec: [009-conditional-robots-noindex-staging.md](../features/009-conditional-robots-noindex-staging.md)
Branch: `feature/conditional-robots-noindex-for-staging`, from `feature/conditional-http-basic-auth-for-staging` (PR #1587)

## Summary

With `BLOCK_ROBOTS=true` in the root `.env`, the `www-static` (app) and `www-docs` (uploads) nginx servers send `X-Robots-Tag: noindex, nofollow` on every response, error responses included. Any other value sends no header, so production needs no change. The switch is independent of `USE_AUTHENTICATION` and uses the same template/`map` mechanism as the conditional basic auth (spec 008).

## Changes

- `conf/nginx/templates/robots.conf.template` (new): `map "${BLOCK_ROBOTS}" $robots_tag { default ""; true "noindex, nofollow"; }`. nginx omits headers whose value is empty.
- `conf/nginx/app/app.conf`: `include /etc/nginx/robots.conf;` and a server-level `add_header X-Robots-Tag $robots_tag always;`.
- `conf/nginx/docs/docs.conf`: the same include and header.
- `docker-compose.yml`:
  - `www-static`: env `BLOCK_ROBOTS=${BLOCK_ROBOTS:-}`. The templates dir mount and output dir already come from 008.
  - `www-docs`: mounts only `robots.conf.template`, read-only. The auth template would leave `${USE_AUTHENTICATION}` unrendered there and nginx would fail. Env `BLOCK_ROBOTS` and `NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx`.
- `.env-TEMPLATE`: `BLOCK_ROBOTS=` with comments.
- `README.md`: new section "Search engine blocking (X-Robots-Tag)". It covers the mechanism, the `add_header` inheritance caveat, and why there is no `robots.txt`.

## Verification

- Throwaway `nginx:1.30-alpine` containers with the same mounts and env as the compose services:
  - **App, all 6 combinations** of `USE_AUTHENTICATION` (`true`/empty) × `BLOCK_ROBOTS` (`true`/`false`/empty): `nginx -t` passes. With `true`, the header appears on `/` (`401` with auth, `502` without upstream), `/static/` (`404`) and `/api/` (`302`). With `false` or empty, there is no header. Auth behaves the same regardless of `BLOCK_ROBOTS`.
  - **Docs:** only `robots.conf` is rendered. With `true`, the header is on `/doc.pdf` (`200`) and on a missing file (`404`). With empty, there is no header. The existing security headers are still sent.
- `docker compose config -q` passes. `BLOCK_ROBOTS` renders on both services, and so does the docs template mount.
- `make dev_test`: green (253 tests, 5 skipped).

## Pending

- Staging, after deploy with `BLOCK_ROBOTS=true`: `curl -I https://<staging>/` and `curl -I https://<staging-docs>/<file>` show the header. Production shows none.
