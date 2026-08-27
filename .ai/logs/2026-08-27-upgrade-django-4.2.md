# 2026-08-27 — Django Upgrade Phase 4: Django 3.2 → 4.2 LTS (Python 3.12)

Branch: `setup/django-4.2` (from `main`). Plan: `.ai/plans/018-upgrade-django-phase4-django-4.2.md`.

## Changes

### Version bumps

- `Dockerfile`: `python:3.10-alpine` → `python:3.12-alpine`
- `requirements.txt`: `Django==3.2.25` → `Django==4.2.30`, `jsonfield==3.1.0` → `jsonfield==3.2.0`, `django-rosetta==0.9.9` → `django-rosetta==0.10.3`
- `requirements-dev.txt`: unchanged (all pins already 4.2-compatible)
- `make dev_build` clean on Python 3.12 — no setuptools/build issues

### Settings cleanup

- `src/fi-admin/settings.py`: removed `USE_L10N = True` (default `True` on 4.2) and dead `TEMPLATE_DEBUG = False`

### DeleteView fix (unplanned — Django 4.0 breaking change caught by tests)

Django 4.0 made `DeleteView` form-based: custom `delete()` overrides are no longer
called on POST, so related-object cleanup silently stopped running (7 test failures).
Renamed `delete(self, request, *args, **kwargs)` → `form_valid(self, form)`
(object available as `self.object`) in:

- `src/leisref/views.py` (`ActDeleteView`)
- `src/title/views.py` (`TitleDeleteView`)
- `src/institution/views.py` (`InstDeleteView`)
- `src/biblioref/views.py` (`BiblioRefDeleteView`)
- `src/oer/views.py` (`OERDeleteView`)
- `src/multimedia/views.py` (`MediaDeleteView`)

`thesaurus` `DescDeleteView`/`QualifDeleteView` mix `DescUpdate`/`QualifUpdate` into
`DeleteView`, so the inherited update `form_class`/`form_valid`/`get_form_kwargs`
hijacked the new form-based delete flow. Overrode `form_class = Form`, dropped the
custom `ths` form kwarg, and added a `form_valid` that deletes and redirects.

### Makefile

- New target `dev_test_deprecations` — runs tests with `python -Wd` (usage: `make dev_test_deprecations app="main api ..."`)

### New tests (`src/biblioref/tests.py`)

`BiblioRefDeleteView` was the only converted delete view with **no** test coverage — the
whole `BiblioRefTest` class is `@skip`-ed ("Figure out why these tests are broken!"), which
is why biblioref stayed green while its delete cleanup was silently broken. Added
`BiblioRefDeleteViewTest` with 3 tests:

- `test_delete_reference` — reference plus its `Descriptor`, `Attachment`, `ReferenceLocal`
  and `ReferenceComplement` are all removed, and the view redirects to the list
- `test_delete_reference_of_another_user_not_allowed` — 401, record kept
- `test_delete_source_with_analytics_not_allowed` — renders `delete_analytics_first.html`, record kept

Regression check: reverting `form_valid` back to `delete()` makes `test_delete_reference`
fail with `ProtectedError`, confirming the test catches the Django 4.0 breakage.

## Verification

- `make dev_test`: full suite green — 223 tests across 13 apps (biblioref: 5 skipped, pre-existing). JSONField behavior unchanged after jsonfield 3.2.0 (biblioref/oer/leisref green).
- `make dev_test_coverage`: all 8 converted delete code paths are executed by tests (biblioref 683-696, institution 367-377, leisref 321-334, multimedia 279-293, oer 308-321, title 418-426, thesaurus 330-338 and 3474-3482 — none appear in coverage's missing-line ranges). Project total 55%.
- Migrations: all existing migrations apply cleanly on SQLite under 4.2 (`migrate --skip-checks`).
- `makemigrations` diff 3.2 vs 4.2 (same code, empty SQLite): the upgrade introduces **only one** new detected change — `title.Title.users` (`related_name="users+"`): Django 4.0 changed how the hidden related name is computed. Metadata-only, no schema impact. **No migration committed.**
- Pre-existing drift (unrelated to the upgrade, identical output under 3.2): ~100 pending `AlterField` operations across attachments, biblioref, classification, database, help, institution, leisref, multimedia, oer, related, thesaurus, title — mostly `choices`/`verbose_name` attribute drift, schema-neutral. Left uncommitted; should be addressed as its own task.

## Blockers / environment notes

- **`make dev_migrate` / `dev_makemigrations` against the remote dev DB is blocked**: `basalto08.bireme.br:6612` (`fi_admin_tst`) is MariaDB **10.3.34**; Django 4.2 requires MariaDB ≥ 10.4 and refuses to connect (`NotSupportedError`). Prod is MySQL 8+ so this only affects the shared dev/test DB — it needs an upgrade (or a local MySQL 8 container) before the dev environment can run against a real DB.
- `makemigrations`/`migrate` also trigger DB access at import time via `src/biblioref/field_definitions.py:11` (module-level `AuxCode` query), so `--skip-checks` alone doesn't avoid the connection.
- `docker compose exec` targets a running container: after `make dev_build`, run `make dev_up` to recreate the container, or commands run against the old image.

## Remaining deprecation warnings (for Phase 5 — Django 5.x)

From `python -Wd manage.py test` over all apps:

1. `RemovedInDjango50Warning` — `tastypie/compat.py:22`: `django.utils.datetime_safe` is deprecated (fixed in django-tastypie ≥ 0.15; bump in Phase 5).
2. `RemovedInDjango50Warning` — form/formset `"default.html"` templates will be removed; `"div.html"` becomes the default renderer in 5.0 (review form templates in Phase 5).
3. `UserWarning` — `deform/template.py:7`: `pkg_resources` deprecated (deform dependency, not Django; watch for removal in newer setuptools).

Non-deprecation warnings observed (pre-existing): unordered pagination on `institution.Institution` list, naive datetime on `Reference.created_time` in one test.

## ✅ Goals met

| Goal                                                      | Status                                                    |
| --------------------------------------------------------- | --------------------------------------------------------- |
| Django 3.2.25 → 4.2.x LTS, Python 3.10 → 3.12             | Django 4.2.30 on `python:3.12-alpine`, image builds clean |
| jsonfield 3.1.0 → 3.2.0, rosetta 0.9.9 → 0.10.x+          | 3.2.0 and 0.10.3                                          |
| Remove `USE_L10N` + dead `TEMPLATE_DEBUG`, after the bump | Both gone from `settings.py` (and the SAMPLE, see below)  |
| Full test suite passes in the 3.12 image                  | 223 tests, 13 apps, all OK                                |
| JSONField behavior unchanged                              | biblioref/oer/leisref green after the jsonfield bump      |
| Django 5.x deprecations logged for Phase 5                | 3 warnings logged, via new `make dev_test_deprecations`   |

## ⚠️ One goal incomplete

**"`make dev_migrate` runs clean"** — I could not run it. The dev/test database at `basalto08.bireme.br:6612` is MariaDB 10.3.34 and Django 4.2 refuses to connect (requires ≥ 10.4). This is an infrastructure blocker, not a code defect. I substituted the strongest available check: all existing migrations apply cleanly on SQLite under 4.2, and I diffed `makemigrations` output between 3.2 and 4.2 on identical code — the upgrade introduces exactly **one** new detected change (`title.users` hidden `related_name`, metadata-only, no schema impact). The other ~100 pending `AlterField`s are pre-existing drift, byte-identical under 3.2.

That DB needs upgrading (or a local MySQL 8 container) before anyone can run the dev environment against a real database. Real-DB verification stays deferred to validation, consistent with the spec's accepted SQLite-only gap.

## ⚠️ Code quality notes

The `delete()` → `form_valid()` conversion is actually **safer** than what it replaced, in a way worth knowing. The old code called `super().get_object()`, which deliberately bypassed each view's own `get_object()` authorization hook. So on an unauthorized POST, the related-object cleanup deletes ran *first* and the request only blew up afterwards, on the auth hook — real data loss on a rejected request. Now `self.object` comes from the overridden `get_object()`, so an unauthorized request fails before any delete happens.

Two pre-existing warts I did **not** touch, since they're outside this feature and unchanged by it:
- `MediaDeleteView.get_object()` and `OERDeleteView.get_object()` *return* `HttpResponse(401)` instead of raising, so an unauthorized request still ends in a 500 rather than a clean 401. Broken before and after; only the data-loss part improved.
- `thesaurus` `get_success_url()` does `'?ths=' + request.GET.get("ths")`, which raises `TypeError` when `ths` is absent.

## 🚫 Scope creep: none material

Everything beyond the plan traces to a goal. The eight DeleteView conversions were forced by the Django 4.0 breakage that the test-suite goal exposed. The `dev_test_deprecations` target is required by the deprecation-logging goal and by CLAUDE.md's "create it in the Makefile" rule. The three biblioref tests close a coverage gap on code this feature changed. The one thing I added during this review — removing `TEMPLATE_DEBUG` from `src/fi-admin/settings_local.py-SAMPLE` — is a one-line extension of the settings-cleanup goal; the sample mirrors `settings.py`'s test block, so leaving it would let anyone copying it reintroduce the dead setting.

No migrations were committed, no unrelated refactors, and coverage artifacts (`src/.coverage`, `src/htmlcov`) are gitignored.

## Verdict: ready to complete

The one caveat to accept consciously: `make dev_migrate` against a real MySQL/MariaDB is unverified and unverifiable until that dev DB is upgraded past 10.4. If you'd rather not merge without it, the fix is on the infrastructure side, not in this branch.

Worth queuing as separate follow-ups: the MariaDB 10.3 upgrade, and the 5 biblioref tests still sitting behind `@skip("Figure out why these tests are broken!")` — that skip is exactly why the delete regression slipped through unnoticed.

Run `/feature complete` when ready to merge, or `/feature pr` to open a pull request first.
