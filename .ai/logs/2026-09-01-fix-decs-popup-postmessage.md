# Fix DeCS lookup popup broken after Django 4.2 upgrade

## Problem

After commit `5d2e234` (Upgrade to Django 4.2 LTS), the DeCS descriptor selection
popup opened by `decs_search()` (used in several form templates) stopped returning
the selected descriptor. The popup window console showed:

```
Uncaught TypeError: Cannot read properties of null (reading 'postMessage')
    at postMsg (locate/?lang=pt&mode=dataentry&tree_id=...)
```

## Cause

Django 4.0 introduced `SECURE_CROSS_ORIGIN_OPENER_POLICY`, defaulting to
`same-origin`. `SecurityMiddleware` (already enabled) now sends
`Cross-Origin-Opener-Policy: same-origin` on every response.

That header severs the opener relationship for popups on a different origin, so in
the DeCS locator window (`https://decs-locator.bvsalud.org/...`) `window.opener`
is `null` and its `postMsg()` call fails.

## Change

`src/fi-admin/settings.py`: set

```python
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'
```

This keeps the protection for windows that open fi-admin, while allowing popups
opened *by* fi-admin (the DeCS lookup) to retain `window.opener` and post the
selected descriptor back.

## Verification

- `make dev_check` — System check identified no issues.
