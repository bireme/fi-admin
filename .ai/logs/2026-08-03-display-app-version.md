# Display the Application Version in the Footer

Implementation of `.ai/plans/016-add-application-version.md`.

## Changes

### Build-time propagation
- `Makefile`: `export APP_VERSION` so Docker Compose can read it.
- `Dockerfile` (base stage): `ARG APP_VERSION=unknown` + `ENV APP_VERSION=${APP_VERSION}`;
  the `dev` and `prod` stages inherit the `ENV`.
- `docker-compose.yml`, `docker-compose-dev.yml`, `docker-compose-api.yml`:
  pass `args: APP_VERSION: ${APP_VERSION:-unknown}` to the build.

### Django configuration
- `src/fi-admin/settings.py`: `APP_VERSION = os.environ.get("APP_VERSION", "unknown")`
  and added `APP_VERSION` to `TEMPLATE_VISIBLE_SETTINGS` (exposed by the existing
  `utils.context_processors.django_settings`).

### Footer display
- `src/templates/base.html`: `<div class="app-version">v{{ APP_VERSION }}</div>` inside
  the existing `.terms_politic` block. Not translated — the `v1.2.3` format is language-neutral.
- `src/static/css/screen.css`: `#footer .app-version` rule (right aligned, 11px, subdued grey).

### API consolidation
- `src/api/bibliographic.py`: `system_version` now comes from `settings.APP_VERSION`;
  removed `_version_cache` and the unused `os` import.
- Deleted `src/templates/version.txt` (stale, `1.25.0-23`).
- `fabric/fabfile.py`: removed `update_version_file()` and its callers in `full_update()` /
  `update()`, plus the `git checkout .../version.txt` step. Docker/Make is the canonical
  deployment workflow.

### Tests
- `src/dashboard/tests.py`: `test_footer_shows_app_version` with
  `@override_settings(APP_VERSION="9.8.7-test")` asserting the rendered footer contains `v9.8.7-test`.
- `src/api/tests.py`: `test_detail_reports_system_version_from_settings` bakes a
  `ReferenceSource` and asserts `system_version == "9.8.7-test"`.
  The fixture must set `literature_type` and `publication_date_normalized` because
  `ReferenceSource.__str__` (`src/biblioref/models.py:239`) indexes `literature_type[0]`
  during serialization.

## Verification

- `make dev_test_app app=api` → 36 tests, OK.
- `make dev_test_app app=dashboard` → 5 tests, OK.
- Running dev container: `APP_VERSION=2.4.2-rc-3.2`, `settings.APP_VERSION=2.4.2-rc-3.2`,
  matching `make tag` (`bireme/fi-admin:2.4.2-rc-3.2`).
- `curl http://localhost:8000/` renders `v2.4.2-rc-3.2` in the footer.
- With `APP_VERSION` unset in the container, `settings.APP_VERSION` falls back to `unknown`.

### Not verified locally
- Fresh `make dev_build` / prod / API image builds: the local Docker daemon has no working
  DNS inside build containers (`apk` fails with `DNS: transient error`), unrelated to these
  changes. Verification used the already-running dev image, which carries the expected
  `APP_VERSION` env var.
