FI-ADMIN
=========

Administration interface and API for Information Sources.

Dependencies (uv)
-----------------

Python dependencies are managed with [uv](https://docs.astral.sh/uv/) in `src/pyproject.toml` + `src/uv.lock`.
Every command runs through `uv run` (e.g. `uv run python manage.py check`).

- Add or change a dependency: edit `src/pyproject.toml`, then run `make dev_lock` to regenerate `src/uv.lock`
- Upgrade to the newest allowed patch releases: `make dev_lock_upgrade` (or `make dev_lock_upgrade package=django`),
  then run `make dev_test`
- Sync the dev venv with the lock: `make dev_sync` (`uv run` in the dev container also syncs before running)
- The dev venv is `src/.venv`. It is created **only inside the dev container** (Alpine/musl):
  never run `uv sync` on the host, since a host venv won't work in the container
- `src/.venv` is owned by root (the dev container runs as root). Remove it with
  `make dev_exec cmd="rm -rf .venv"` or `sudo`
- Inside Dropbox, keep it out of sync with `attr -s com.dropbox.ignored -V 1 src/.venv`

Staging access protection (HTTP basic auth)
-------------------------------------------

The `www-static` nginx (`docker-compose.yml`) can require HTTP basic auth on the Django app (`location /`),
to keep a staging/test environment private. `/static/` and the `/api/` redirect stay public.

- Enable it with `USE_AUTHENTICATION=true` in the root `.env`. Any other value (unset, empty, `false`) keeps it off,
  so production needs no change
- Create or update a user with `make htpasswd user=<name>` (prompts for the password; bcrypt entry saved in the
  gitignored `conf/nginx/.htpasswd`), then `make prod_up`
- On hosts without auth, `touch conf/nginx/.htpasswd` before the first `make prod_up`; otherwise docker creates an
  empty directory at that path (harmless while auth is off, but `make htpasswd` will ask you to remove it)
- How it works: `conf/nginx/templates/variables.conf.template` maps `USE_AUTHENTICATION` to `$auth_enable`; the
  nginx image renders it to `/etc/nginx/variables.conf` at startup (`NGINX_ENVSUBST_OUTPUT_DIR`), included by
  `conf/nginx/app/app.conf`
