# Silence pkg_resources deprecation warning

## Changes
- `docker-compose-dev.yml`: added `PYTHONWARNINGS=ignore:pkg_resources is deprecated:UserWarning`
  to the `fi_admin` service environment.
- `docker-compose.yml`: same variable added to the `fi_admin` and `cron` services.
- `docker-compose-api.yml`: same variable added to the `fi_admin_api` service.

## Why
`deform/template.py` imports `pkg_resources`, which emits a UserWarning on every
`manage.py` invocation (runserver, clearsessions, etc.). The filter hides only that warning.

## Notes
- In list-style `environment:` entries, do not quote the value — quotes become part of it.
- Follow-up: setuptools >= 81 removes `pkg_resources`, which would break `deform`.
  Consider pinning `setuptools<81` until deform drops the dependency.
