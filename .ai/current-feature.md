# Current Feature: Cache-busting version parameter for screen.css

## Status

In Progress

## Goals

- `src/static/css/screen.css` is loaded with a version query parameter (e.g. `css/screen.css?v=<version>`) so browsers fetch the new file whenever the stylesheet changes, instead of serving a stale cached copy
- All templates that load `screen.css` use the versioned URL: `src/templates/base.html`, `src/templates/suggest/invalid-link.html`, `src/templates/suggest/thanks.html`
- The version is controlled from one place (no hand-edited `?v=` literals scattered across templates)
- The version changes on each release/deploy (or when the stylesheet content changes) and stays stable otherwise, so normal caching still works between releases
- Works in dev (`runserver`) and prod (gunicorn + collected static) without extra manual steps
- Tests cover the versioned URL rendering; `make dev_test` stays green
- Log written in `.ai/logs/`

## Notes

- Inline description: "Implement a version parameter to control the load of the screen.css and avoid user cache when changes are made in the stylesheet"
- Existing hook: `APP_VERSION` (`src/fi-admin/settings.py:21`, from env; set by `Makefile` from branch/tag, passed via Dockerfile `ARG`/`ENV` and the compose files) is already exposed to templates via `TEMPLATE_VISIBLE_SETTINGS` + `utils.context_processors.django_settings` and shown in the footer (`base.html:61`). Reusing it as `?v={{ APP_VERSION }}` is the simplest option
- Caveat: `APP_VERSION` defaults to `unknown` (dev, or when unset) → constant value, no busting; consider a fallback (e.g. file mtime/content hash) or a dedicated `STATIC_VERSION` setting
- Alternatives to weigh in `plan`: a small template tag/filter appending a version (hash or mtime) to any static path; Django `ManifestStaticFilesStorage` (hashed filenames for all static files — broader change, needs `collectstatic`, affects every `{% static %}` URL)
- Other stylesheets/scripts (bootstrap, JS) are out of scope unless the chosen mechanism covers them for free
- Use Makefile targets for all build/test/manage commands (CLAUDE.md)
- Decision 2026-10-28 (plan): custom `{% versioned_static %}` tag (content md5[:8] as `?v=`, no new dependency) instead of `ManifestStaticFilesStorage` — Manifest would break collectstatic on dangling CSS refs (`logo-BIREME.png`, jquery-ui icons, `.map` files), needs collectstatic before gunicorn start and a test storage override; Docker is the only deploy target (fabfile ignored)
- Result 2026-10-28: implemented; `make dev_test` green (253 tests, 5 skipped); pending: `make dev_check` and browser check (dev DB 172.17.1.20 unreachable)
- Log: [2026-10-28-versioned-static-screen-css.md](.ai/logs/2026-10-28-versioned-static-screen-css.md)

## Detailed Plan

[023-versioned-static-screen-css.md](.ai/plans/023-versioned-static-screen-css.md)

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
- 2026-10-06: Completed "Django Upgrade Phase 5.0 — Fix Django 5.x Deprecations on 4.2" — merged to `main` (PR #1578); commit `cf369f75`
- 2026-10-06: Loaded "Django Upgrade Phase 5.1 — Keep jsonfield" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) task 5.1
- 2026-10-06: Starting "Django Upgrade Phase 5.1 — Keep jsonfield" — following plan [019-keep-jsonfield-django-5.2.md](.ai/plans/019-keep-jsonfield-django-5.2.md)
- 2026-10-06: Loaded "Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) tasks 5.2 and 5.3
- 2026-10-06: Starting "Django Upgrade Phases 5.2 & 5.3 — Python 3.14 + Django 5.2 dependency bumps" — following plan [020-upgrade-python-3.14-django-5.2-deps.md](.ai/plans/020-upgrade-python-3.14-django-5.2-deps.md)
- 2026-10-06: Phases 5.2 & 5.3 "Python 3.14 + Django 5.2 dependency bumps" implemented; commit `39b95b46` on `feature/django-upgrade-phase-5.2-5.3` (not yet merged)
- 2026-10-06: Loaded "Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations" — following plan [001-upgrade-django-to-5.2.md](.ai/plans/001-upgrade-django-to-5.2.md) tasks 5.4–5.6
- 2026-10-06: Starting "Django Upgrade Phases 5.4, 5.5 & 5.6 — Django 5.x breaking changes, tastypie checks, migrations" — following plan [021-django-5.2-breaking-changes-tastypie-migrations.md](.ai/plans/021-django-5.2-breaking-changes-tastypie-migrations.md)
- 2026-10-06: Phases 5.4–5.6 "Django 5.x breaking changes, tastypie checks, migrations" implemented; commit `2f3d95a3` on `validation` (pending manual checks: `rebuild_index`, browser smoke)
- 2026-10-06: Loaded "Replace pip with uv as package manager" — following spec [007-replace-pip-with-uv.md](.ai/features/007-replace-pip-with-uv.md)
- 2026-10-07: Starting "Replace pip with uv as package manager" — following plan [022-replace-pip-with-uv.md](.ai/plans/022-replace-pip-with-uv.md)
- 2026-10-07: Completed "Replace pip with uv as package manager" — merged to `main` (PR #1584); commit `ab7f7bb5`
- 2026-10-28: Loaded "Cache-busting version parameter for screen.css" — inline description
- 2026-10-28: Starting "Cache-busting version parameter for screen.css" on `feature/cache-busting-version-parameter-for-screen-css` (from `feature/sidebar-menu-and-dashboard-polish`) — following plan [023-versioned-static-screen-css.md](.ai/plans/023-versioned-static-screen-css.md)
