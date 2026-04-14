# 2026-04-14 — Add User-Agent header to EmailModelBackend

## Summary

Added a hardcoded `User-Agent` header to the outgoing `requests.post` call in `EmailModelBackend.authenticate` so that upstream proxies/WAFs do not block the default `python-requests/x.y.z` UA.

## Changes

- `src/biremelogin/authenticate.py`
  - Added module-level constant `USER_AGENT = "fi-admin/2.3 (+https://fi-admin.bvsalud.org)"`
  - Added `'User-Agent': USER_AGENT` to the `headers` dict passed to `requests.post`
  - Removed stray `print(r.text)` debug statement

## Out of Scope (unchanged)

- No new Django settings.
- No other headers added (`Accept-Encoding`, `Accept-Language`, etc.).
- No changes to request body, URL, auth logic, or superuser short-circuit.

## Spec

`.ai/features/002-add-user-agent-header-to-biremelogin.md`
