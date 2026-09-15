# Configure CSRF trusted origins

## Changes

- Added `DJANGO_CSRF_TRUSTED_ORIGINS` environment support in Django settings,
  parsing comma-separated origins, trimming whitespace and ignoring empty entries.
  The default is an empty list.
- Documented the variable in `conf/app-env-TEMPLATE` and added test-environment
  configuration and Makefile deployment instructions to the README.
- Kept CSRF middleware and token validation enabled.

## Validation

- `make dev_check`: passed with no Django system-check issues; emitted an existing
  dependency warning about `pkg_resources`.
- Used `make dev_exec` to exercise Django CSRF middleware: the configured HTTPS
  test origin with a valid token passed; an untrusted origin and a missing token
  each returned 403. Verified multiple origins, whitespace, blank entries, and
  an unset variable. An initial multiline command failed shell parsing; the
  corrected single-line invocation passed.

## Deployment

On the test server, set
`DJANGO_CSRF_TRUSTED_ORIGINS=https://fi-admin.teste.bvsalud.org` in `conf/app-env`,
deploy the updated code, and run `make prod_build` followed by `make prod_up`.
The remote environment was not modified or verified in this session.
