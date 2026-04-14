# Add User-Agent header to EmailModelBackend

## Problem

`EmailModelBackend.authenticate` in `src/biremelogin/authenticate.py` calls `requests.post` without a `User-Agent` header. The `requests` library defaults to `python-requests/x.y.z`, which proxies/WAFs commonly block, preventing the login flow from reaching the BIREME auth API.

## Goal

Add a minimal, descriptive `User-Agent` header to the outgoing auth request so it is not filtered by upstream proxies.

## Scope

- File: `src/biremelogin/authenticate.py`
- Change: add `User-Agent` to the `headers` dict on the `requests.post` call (line 27–29).

## Decisions

- **User-Agent value:** hardcoded descriptive identifier `fi-admin/1.0 (+https://fi-admin.bvsalud.org)`. Honest, non-browser-spoofing.
- **Other headers:** none. Keep minimal. `Content-Type` and `Accept` stay as-is.
- **Configuration:** hardcoded module-level constant, not a Django setting. Matches the existing style in this module.

## Acceptance Criteria

- `headers` dict in `authenticate.py` includes `User-Agent` set to the descriptive string.
- No new Django settings introduced.
- No change to request body, URL, or other headers.
- Existing auth flow (superuser short-circuit, success path, failure path) unchanged.

## Out of Scope

- Mimicking a browser UA.
- Adding `Accept-Encoding`, `Accept-Language`, or other proxy-hint headers.
- Refactoring the backend beyond the header addition.
