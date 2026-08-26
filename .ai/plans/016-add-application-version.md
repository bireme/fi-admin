# Display the Application Version in the Footer

## Summary

Bake the Makefile’s `APP_VERSION` into each Docker image, expose it through Django settings, and display `v{{ APP_VERSION }}` in the shared HTML footer. Use the same setting for the API’s existing `system_version` field, replacing the stale generated version file.

## Implementation

1. Build-time propagation

   - In `Makefile`, export the existing `APP_VERSION` so Docker Compose can use it.
   - In `docker-compose.yml`, `docker-compose-dev.yml`, and `docker-compose-api.yml`, pass `APP_VERSION` as a build argument.
   - In the Dockerfile’s base stage:
     - Declare `ARG APP_VERSION=unknown`.
     - Persist it as `ENV APP_VERSION=${APP_VERSION}`.
   - Both development and production image stages will inherit the value.

2. Django configuration

   - Define `APP_VERSION = os.environ.get("APP_VERSION", "unknown")` in `src/fi-admin/settings.py`.
   - Add `APP_VERSION` to `TEMPLATE_VISIBLE_SETTINGS`.
   - Reuse the existing `django_settings` context processor; no new processor is needed.

3. Footer display

   - In `src/templates/base.html`, add `v{{ APP_VERSION }}` beneath the terms and privacy links.
   - Add a small `.app-version` rule in `src/static/css/screen.css` for spacing, subdued color, and right alignment consistent with the existing footer.
   - Do not add translatable text because the `v1.2.3` format is language-neutral.

4. API consolidation

   - Update `ReferenceResource.full_dehydrate()` in `src/api/bibliographic.py` to assign `settings.APP_VERSION` to `system_version`.
   - Remove `_version_cache` and the now-unused `os` import.
   - Delete `src/templates/version.txt`.
   - Remove the obsolete version-file generation and checkout operations from `fabric/fabfile.py`, since Docker/Make is now the canonical deployment workflow.

## Interfaces and Compatibility

- New Docker build argument: `APP_VERSION`, defaulting to `unknown`.
- New container environment variable: `APP_VERSION`.
- New globally available Django template variable: `APP_VERSION`.
- The bibliographic API’s `system_version` field remains present and retains its existing shape; only its source changes.
- No database or URL changes are required.

## Tests and Verification

- Add a dashboard rendering test using `override_settings(APP_VERSION="9.8.7-test")` and assert that the footer contains `v9.8.7-test`.
- Add a bibliographic API detail test that overrides the setting and asserts `system_version == "9.8.7-test"`.
- Run tests through the existing Make target, targeting the dashboard and API test modules.
- Build through the Make targets to validate the Docker argument in development, production, and API Compose configurations.
- Start the development environment through Make and verify that:
  - `make tag` and the footer report the same version.
  - The bibliographic API reports the same version.
  - An image built without the argument reports `unknown`.
- Create `.ai/logs/2026-08-03-display-app-version.md` summarizing the implementation and verification results.

## Assumptions

- Docker and Make are the supported deployment path; the legacy Fabric deployment flow is retired.
- The displayed value identifies the built image, so a new commit requires rebuilding the image to update the version.
- Templates that intentionally override the footer with an empty block will continue hiding it.
- Missing build metadata is shown as `vunknown` in the footer and `unknown` in the API.
