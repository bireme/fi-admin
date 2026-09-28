# Current Feature: Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2

## Status

In Progress

## Goals

- `make dev_test_deprecations` (all apps) shows **zero** `RemovedInDjango` warnings, and no naive-datetime `RuntimeWarning` or `UnorderedObjectListWarning`
- Only remaining warning: deform's `pkg_resources` UserWarning, documented as a known upstream issue
- Logout is a POST `<form>` with `{% csrf_token %}` in `menu.html`, styled like the old link, covered by a new test (POST → redirect to `/`, user anonymous)
- `django-tastypie` 0.14.7 → 0.15.1, and the `api` tests pass
- `django-debug-toolbar` 4.3.0 → latest 5.2.x; it still works in dev with `DEBUG_TOOLBAR=1`, and is disabled whenever `test` is in `sys.argv`
- setuptools pinned `<81` in the Dockerfile, and the image builds (`make dev_build`)
- Institution list per-user branch has explicit `order_by('-id')`
- Full suite passes (`make dev_test`), ≥ 223 tests plus new ones
- Plan `001-upgrade-django-to-5.2.md` updated (5.0 item ticked; logout/tastypie/toolbar marked done early), and a log written in `.ai/logs/`

## Notes

- Spec: [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
- Branch: `setup/django-5.2` (current). Django stays on 4.2.x in this feature
- Baseline (2026-09-28): 223 tests OK (skipped=5). The warnings were tastypie `datetime_safe`, form `default.html` (from debug-toolbar 4.3.0 only, not app code), deform `pkg_resources`, naive datetime in `biblioref/tests.py`, and unordered pagination in `institution/views.py`. GET logout (`menu.html:130`) is not hit by any test
- Disable the toolbar at `src/fi-admin/settings.py:9` (`… and 'test' not in sys.argv`), because the `if 'test'` block runs after the toolbar is registered at line 379. `urls.py:102` reads the same flag
- Gate is a manual check (no strict Makefile target), per the user's decision
- After requirement/Dockerfile changes: `make dev_build && make dev_up`
- Implementation order: toolbar off in tests → biblioref datetimes + institution ordering → POST logout + test → setuptools pin, debug-toolbar bump, tastypie bump (last, to isolate API regressions) → verify, update plan, write log
- Out of scope: the Django 5.2 bump, the Python 3.13/3.14 image, `RemovedInDjango60Warning` items, replacing deform, and changing the password hasher

## Detailed Plan

- `.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md` (spec with tasks A–H)
- `.ai/plans/001-upgrade-django-to-5.2.md` (Phase 5, task 5.0)

## History

- 2026-04-13: Completed "Add indexed_database filter to LeisRef API" — filter legislation by database acronym via ?indexed_database param
- 2026-04-14: Completed "Add User-Agent header to EmailModelBackend" — hardcoded `fi-admin/2.3` UA in `src/biremelogin/authenticate.py` to avoid proxy blocks
- 2026-05-27: Starting "Django Upgrade Phase 2 — Deprecation Fixes" — following spec [003-upgrade-django-phase2-deprecation-fixes.md](.ai/features/003-upgrade-django-phase2-deprecation-fixes.md)
- 2026-07-17: Completed "Django Upgrade Phase 2 — Deprecation Fixes" — merged into `rc/3.2` flow; commit `4ee052a`
- 2026-07-17: Starting "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — following spec [004-upgrade-django-phase3-django-3.2.md](.ai/features/004-upgrade-django-phase3-django-3.2.md)
- 2026-08-27: Completed "Django Upgrade Phase 3 — Django 2.2 → 3.2 LTS" — merged to `main`; commit `c0ba51a`
- 2026-08-27: Starting "Django Upgrade Phase 4 — Django 3.2 → 4.2 LTS" — following plan [018-upgrade-django-phase4-django-4.2.md](.ai/plans/018-upgrade-django-phase4-django-4.2.md)
- 2026-09-28: Phase 4 "Django 3.2 → 4.2 LTS" implemented; commit `5d2e234a` is on `validation` (not yet merged to `main`)
- 2026-09-28: Loaded "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — following spec [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
- 2026-09-28: Starting "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" on `setup/django-5.2` — following spec [006-upgrade-django-phase5.0-fix-deprecations.md](.ai/features/006-upgrade-django-phase5.0-fix-deprecations.md)
