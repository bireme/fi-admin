# Feature Spec 008: Conditional HTTP Basic Authentication for Staging

## Summary

Protect the fi-admin staging environment from public access with nginx HTTP Basic Authentication. An environment variable (`USE_AUTHENTICATION`) turns it on or off, and it mirrors the implementation already used in **iahx-opac** (commit `747764d`, "Add http basic authentication for use in test environment").

## Reference implementation (iahx-opac)

- `docker/nginx/templates/variables.conf.template`:
  ```nginx
  map "${USE_AUTHENTICATION}" $auth_enable {
      default     "off";
      true        "Restrict Access";
  }
  ```
  The official nginx image (≥ 1.19) renders it with envsubst at container start.
- `nginx.conf`, inside the dynamic location only:
  ```nginx
  auth_basic $auth_enable;
  auth_basic_user_file /etc/nginx/.htpasswd;
  ```
- `docker-compose.yml` (webserver service): mounts `./docker/nginx/templates:/etc/nginx/templates` and `./docker/nginx/.htpasswd:/etc/nginx/.htpasswd`, and sets `USE_AUTHENTICATION=${USE_AUTHENTICATION}`.
- `.htpasswd` is gitignored. `.env` (staging) has `USE_AUTHENTICATION=true`; `.env.prod` has `false`.

## Decisions

| # | Topic | Decision |
|---|-------|----------|
| 1 | Scope | Only the main app stack: the `www-static` service in `docker-compose.yml` (`conf/nginx/app/app.conf`). `www-docs` and the API stack (`docker-compose-api.yml`) are **out of scope**. The API stack is excluded because tastypie `ApiKeyAuthentication` may use the `Authorization` header, and because staging API consumers would break. |
| 2 | Protected locations | Only `location /` (proxied Django app), mirroring iahx-opac, which protects only the front controller. `/static/` and the `/api/` redirect stay public. |
| 3 | Credentials file | `conf/nginx/.htpasswd`, gitignored, mounted read-only at `/etc/nginx/.htpasswd`. Created or updated with a new Makefile target `make htpasswd user=<name>`, which runs `docker run --rm -it httpd:2.4-alpine htpasswd -nB <user>`. The password is entered at a prompt (bcrypt) and never passed on the command line. |
| 4 | Toggle semantics | Only the exact value `USE_AUTHENTICATION=true` enables auth. Unset, empty or any other value means **off**, so existing prod `.env` files need no change. Realm: `"Restrict Access"`. The variable lives in the root `.env` that docker-compose reads, not in `conf/app-env`. |
| 5 | Verification | Manual check on staging after deploy (see Acceptance Criteria). No nginx-check Makefile target. `make dev_test` must stay green. |

## Implementation outline

1. **`conf/nginx/templates/variables.conf.template`** (new): the same `map` block as iahx-opac.
2. **`conf/nginx/app/app.conf`**:
   - At the top (http context, before `upstream`): `include /etc/nginx/variables.conf;`
   - Inside `location /`: `auth_basic $auth_enable;` and `auth_basic_user_file /etc/nginx/.htpasswd;`, with a comment noting it is conditional on `USE_AUTHENTICATION`.
3. **`docker-compose.yml`** (`www-static` service):
   - volumes: `./conf/nginx/templates:/etc/nginx/templates:ro`, `./conf/nginx/.htpasswd:/etc/nginx/.htpasswd:ro`
   - environment: `USE_AUTHENTICATION=${USE_AUTHENTICATION}`, `NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx`
   - Why the output dir: `conf.d` is bind-mounted from `conf/nginx/app`. With the default output dir (`/etc/nginx/conf.d`), the rendered `variables.conf` would be written into the repo on the host as a root-owned file. Rendering to `/etc/nginx` keeps it inside the container. (Implementation note: `/etc/nginx/vars` was the original choice, but the entrypoint skips rendering when the output dir doesn't exist, so an existing writable dir is required.)
4. **`.gitignore`**: add `.htpasswd`.
5. **`Makefile`**: add the `htpasswd` target (requires `user=`; appends to `conf/nginx/.htpasswd` and creates it if missing). Add a help/comment line.
6. **`.env-TEMPLATE`**: add `USE_AUTHENTICATION=` with a comment: `true` on staging enables basic auth, leave empty or `false` in production. Point to `make htpasswd`.
7. **README**: a short "Staging access protection" section covering the variable, the Makefile target, and the note that hosts without auth should `touch conf/nginx/.htpasswd`. If the file is missing, Docker creates an empty directory at the mount path. That is harmless while auth is off, because nginx only reads the file when auth is enabled.
8. **Log** in `.ai/logs/`.

## Acceptance Criteria

- [ ] With `USE_AUTHENTICATION=true` and a valid `.htpasswd`:
  - `curl -I https://<staging>/` returns `401` with `WWW-Authenticate: Basic realm="Restrict Access"`.
  - `curl -I -u user:pass https://<staging>/` returns `200` or `302` (login redirect).
  - `curl -I https://<staging>/static/css/screen.css` returns `200` without credentials.
- [ ] With `USE_AUTHENTICATION` unset, empty or `false`, behavior is unchanged: no auth prompt anywhere.
- [ ] `www-static` starts cleanly in both modes: no nginx config errors in `docker compose logs www-static`, and no `variables.conf` written into `conf/nginx/app/` on the host.
- [ ] `make htpasswd user=<name>` creates or appends a bcrypt entry without exposing the password in the command line.
- [ ] `.htpasswd` is gitignored. `.env-TEMPLATE` and the README document the variable and the target.
- [ ] `make dev_test` stays green (no Django changes expected).
- [ ] Log written in `.ai/logs/`.

## Out of scope

- `www-docs` (uploads domain) and the API stack (`docker-compose-api.yml`, nginx 1.18).
- Dev environment (`runserver`, no nginx).
- Django-level auth middleware or IP allowlists.
