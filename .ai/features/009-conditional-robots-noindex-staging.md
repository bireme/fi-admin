# Feature Spec 009: Conditional `X-Robots-Tag: noindex, nofollow` for Staging

## Summary

Keep search engines from indexing the fi-admin staging environment. When `BLOCK_ROBOTS=true`, nginx sends an `X-Robots-Tag: noindex, nofollow` response header. The switch uses the same mechanism as the conditional basic auth from spec [008](008-conditional-basic-auth-staging.md): an nginx envsubst template defines a `map` from the env var to an nginx variable, and only the exact value `true` enables it.

## Context

- Builds on spec 008 (PR #1587, branch `feature/conditional-http-basic-auth-for-staging`, not merged yet). That branch provides:
  - `conf/nginx/templates/variables.conf.template` (auth `map`);
  - the `templates` mount and `NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx` on `www-static`;
  - `include /etc/nginx/variables.conf;` in `conf/nginx/app/app.conf`.
- iahx-opac has no `X-Robots-Tag`; it only mounts a static `robots.txt`. fi-admin has no robots handling today. This feature reuses only iahx-opac's *conditional mechanism*.
- nginx does not send an `add_header` whose value is an empty string. With the variable off, the map returns `""` and no header is emitted.
- `add_header` inheritance: directives at `server` level apply to a location only if that location has no `add_header` of its own. In `app.conf` and `docs.conf` every `add_header` is at server level and no location defines any, so a server-level header covers all paths, including `/static/` and the `/api/` redirect.

## Decisions

| # | Topic | Decision |
|---|-------|----------|
| 1 | Switch | A **separate** env var, `BLOCK_ROBOTS`, independent of `USE_AUTHENTICATION`. Only the exact value `true` enables it; unset, empty or any other value means off, so production `.env` needs no change. It lives in the root `.env` (compose interpolation). |
| 2 | Scope | `www-static` (`conf/nginx/app/app.conf`) **and** `www-docs` (`conf/nginx/docs/docs.conf`, uploaded files: the PDFs most likely to be indexed). The API stack (`docker-compose-api.yml`, nginx 1.18 without template support) is **out of scope**. |
| 3 | Mechanism | Response header only: `add_header X-Robots-Tag $robots_tag always;` at `server` level with value `"noindex, nofollow"`. **No `robots.txt`**: a `Disallow: /` would stop crawlers from fetching pages and seeing the `noindex`, so URLs they already know could stay indexed. The header also covers non-HTML files (PDFs) on `www-docs`. |
| 4 | Branch | Branch from `feature/conditional-http-basic-auth-for-staging`. The PR targets that branch, or `main` once #1587 is merged. |
| 5 | Template layout | A **new** `conf/nginx/templates/robots.conf.template`, separate from the auth `variables.conf.template`. `www-docs` mounts only the robots template file. Rendering the auth template there would leave `${USE_AUTHENTICATION}` as-is, because the var isn't defined in that container, and nginx would fail on the unknown variable. |

## Implementation outline

1. **`conf/nginx/templates/robots.conf.template`** (new):
   ```nginx
   # Only BLOCK_ROBOTS=true sends X-Robots-Tag; an empty value means nginx omits the header.
   map "${BLOCK_ROBOTS}" $robots_tag {
       default     "";
       true        "noindex, nofollow";
   }
   ```
2. **`conf/nginx/app/app.conf`**:
   - `include /etc/nginx/robots.conf;` next to the existing `include /etc/nginx/variables.conf;`
   - `add_header X-Robots-Tag $robots_tag always;` with the other server-level security headers
3. **`conf/nginx/docs/docs.conf`**:
   - `include /etc/nginx/robots.conf;` at the top (http context)
   - `add_header X-Robots-Tag $robots_tag always;` at server level
4. **`docker-compose.yml`**:
   - `www-static`: env `BLOCK_ROBOTS=${BLOCK_ROBOTS:-}`. The templates dir mount and `NGINX_ENVSUBST_OUTPUT_DIR` are already there from 008.
   - `www-docs`: mount `./conf/nginx/templates/robots.conf.template:/etc/nginx/templates/robots.conf.template:ro`; env `BLOCK_ROBOTS=${BLOCK_ROBOTS:-}` and `NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx`.
5. **`.env-TEMPLATE`**: `BLOCK_ROBOTS=` with a comment (`true` on staging, empty or `false` in production).
6. **README**: extend the "Staging access protection" section with `BLOCK_ROBOTS`, what it covers (app + docs) and why there is no `robots.txt`.
7. **Log** in `.ai/logs/`.

## Acceptance Criteria

- [ ] Local throwaway `nginx:1.30-alpine` containers with the same mounts and env as `www-static` and `www-docs`:
  - `BLOCK_ROBOTS=true`: `curl -I` on `/`, `/static/…` and `/api/…` (app), and on `/` and any file (docs), all return `X-Robots-Tag: noindex, nofollow`. Error responses (`404`, `401`, `502`) also carry it (`always`).
  - `BLOCK_ROBOTS` unset, empty or `false`: no `X-Robots-Tag` header on any response.
  - `nginx -t` passes in both modes, for both containers.
- [ ] `BLOCK_ROBOTS` and `USE_AUTHENTICATION` are independent: each combination behaves as expected on `www-static`.
- [ ] Existing security headers on both servers are unchanged.
- [ ] `docker compose config -q` passes. `make dev_test` stays green (no Django changes).
- [ ] Staging, after deploy: `curl -I https://<staging>/` and `curl -I https://<staging-docs>/<file>` show the header; production shows none.
- [ ] `.env-TEMPLATE` and README updated; log written in `.ai/logs/`.

## Out of scope

- The API stack (`docker-compose-api.yml`, `conf/nginx/api`).
- `robots.txt` and HTML `<meta name="robots">` tags.
- The dev environment (`runserver`, no nginx).
