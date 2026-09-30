# Phase 5.0: Fix Django 5.x deprecations on Django 4.2 (pre-flight)

## Goal

Before bumping Django to 5.2, remove every `RemovedInDjango50Warning` / `RemovedInDjango51Warning` the code base produces on Django 4.2.x. This covers the warnings reported by `make dev_test_deprecations` and the ones found by reading the code (paths the tests don't exercise). It also fixes the small non-Django warnings seen in the same run. This is the third checkbox of task 5.0 in `.ai/plans/001-upgrade-django-to-5.2.md`. Django itself stays on 4.2.x.

## Branch

`setup/django-5.2` (current branch; it already holds the Phase 5 plan updates).

## Decisions Made (interview 2026-09-28)

- **GET logout: fix now** (pulled forward from plan 5.4). `LogoutView` via GET warns `RemovedInDjango50Warning` on 4.2 and is removed in 5.0. Replace the menu link with a POST form and add a test
- **django-debug-toolbar: bump and disable in tests.** Bump 4.3.0 → 5.2.x (declares Django 4.2–5.2, Python 3.10–3.13; plan 5.3 already wanted 5.x). Also force the toolbar off when running tests: it is the only source of the form `default.html` warning, and the suite runs about 4× faster without it (≈7s vs ≈30s)
- **django-tastypie: bump to 0.15.1 now** (pulled forward from plans 5.3/5.5). It declares Django 4.2–5.2 and removes the `django.utils.datetime_safe` import. Bumping on 4.2 isolates the plan's CRITICAL risk from the Django bump
- **setuptools: pin `<81`.** `deform` 3.0.1 (already the latest release) imports `pkg_resources`, which setuptools 81+ removes. The Dockerfile currently runs `pip install --upgrade setuptools`, unpinned (80.10.2 today), so a future rebuild would break `import deform`. The `pkg_resources` UserWarning is accepted and logged as a known upstream issue
- **Naive datetime in tests: fix** (use aware datetimes)
- **Unordered institution pagination: fix** (explicit ordering)
- **Gate: manual check only.** No strict Makefile target. The acceptance check is that `make dev_test_deprecations` output has zero `RemovedInDjango` lines

## Pre-verified Facts (codebase exploration, 2026-09-28)

Baseline `make dev_test_deprecations app="main events multimedia biblioref leisref institution oer title thesaurus suggest classification error_reporting api"` gives **223 tests, OK (skipped=5)**, with these warnings:

| # | Warning | Source |
|---|---------|--------|
| 1 | `RemovedInDjango50Warning`: `django.utils.datetime_safe` is deprecated | `site-packages/tastypie/compat.py:22` (0.14.7) |
| 2 | `RemovedInDjango50Warning`: form/formset `"default.html"` templates will be removed | **django-debug-toolbar 4.3.0** panel forms (`debug_toolbar/panels/__init__.py` → `forms/utils.py`). Not app code |
| 3 | `UserWarning`: `pkg_resources` is deprecated | `site-packages/deform/template.py:7` |
| 4 | `RuntimeWarning`: `Reference.created_time` received a naive datetime | `src/biblioref/tests.py` lines 428–524: `created_time="1970-01-01 00:00"` string literals (about 10 occurrences) |
| 5 | `UnorderedObjectListWarning`: `institution.Institution` | `src/institution/views.py` `InstGenericListView.get_queryset()`: the "filter by user institution" branch (`filter_owner != "*"` or `user_cc != 'BR1.1'`) returns `object_list.filter(cc_code=user_cc)` with no `order_by`. The other branch already ends in `order_by('-id')` or `order_by('-updated_time')` |

The warning that tests do not catch:

| # | Warning | Source |
|---|---------|--------|
| 6 | `RemovedInDjango50Warning`: log out via GET | `src/templates/menu.html:130`: `<a href="{% url 'auth_logout' %}">` → `src/biremelogin/urls.py` `LogoutView(template_name='authentication/logout.html', next_page='/')`. This is the only logout link in templates. Existing tests call `self.client.logout()` and never hit the view |

Other facts:

- The form `default.html` warning is **not** triggered by app code. With `DEBUG_TOOLBAR=0` and that warning turned into an error (`-W error:...`), all 223 tests pass. There are no `{{ form }}` / `as_table` / `as_p` whole-form renders in `src/templates` (only per-field, `non_field_errors` and `management_form`)
- `DEBUG_TOOLBAR` is read from the environment at `src/fi-admin/settings.py:9`. It is used at `settings.py:379` (INSTALLED_APPS/MIDDLEWARE) and at `src/fi-admin/urls.py:102`. The `if 'test' in sys.argv` block comes **after** line 379, so disabling it there is too late. Gate it at line 9 instead (`… and 'test' not in sys.argv`) so both settings and urls see it off
- There are no Django 5.1 deprecations in code: none of `save()` with positional args, `get_storage_class`, `assertQuerysetEqual`, `assertFormsetError`, `CI*Field`, `index_together`, `make_random_password`, `itercompat`, removed hashers, `USE_L10N`, `DEFAULT_FILE_STORAGE`/`STATICFILES_STORAGE`. `USE_TZ = True` is set explicitly. `PASSWORD_HASHERS` is `MD5PasswordHasher` only (still in 5.2)
- PyPI: `django-tastypie` 0.15.1 declares Django 4.2/5.0/5.1/5.2 and Python 3.10–3.12. `django-debug-toolbar` 5.2.0 declares Django 4.2–5.2 and Python 3.10–3.13 (requires `django>=4.2.9`). Newer toolbar majors (6.x–8.x) exist; 5.2.x is chosen as the conservative target. `deform` 3.0.1 is the latest release
- Pins: `requirements.txt:5 django-tastypie==0.14.7`, `requirements-dev.txt:3 django-debug-toolbar==4.3.0`, `Dockerfile:24 pip install --upgrade pip setuptools`
- The dev container must be rebuilt and recreated after requirement changes: `make dev_build && make dev_up`

## Acceptance Criteria

- [ ] `make dev_test_deprecations` (all apps) output contains **zero** `RemovedInDjango` warnings, and also none of the `RuntimeWarning` naive-datetime or `UnorderedObjectListWarning` warnings
- [ ] The only remaining warning is the `pkg_resources` UserWarning from deform, documented as a known upstream issue
- [ ] Logout is a POST `<form>` with `{% csrf_token %}`, styled like the old menu link. A new test checks that POST to `auth_logout` logs the user out and redirects to `/`
- [ ] `django-tastypie==0.15.1`, and the `api` test suite passes
- [ ] `django-debug-toolbar==5.2.x` (latest 5.2 patch). The toolbar still works in the dev container when `DEBUG_TOOLBAR=1` (not under test)
- [ ] Toolbar disabled whenever `test` is in `sys.argv`
- [ ] setuptools pinned `<81`, and the image builds (`make dev_build`)
- [ ] Institution list has explicit ordering in the per-user branch
- [ ] Full suite passes: `make dev_test`, with a test count ≥ 223 + new tests
- [ ] Plan `001-upgrade-django-to-5.2.md` updated: tick the 5.0 deprecation item, and mark the logout (5.4), tastypie (5.3/5.5) and debug-toolbar (5.3) items as done early
- [ ] Log file in `.ai/logs/`

## Tasks

### A — Disable debug-toolbar under test
**File**: `src/fi-admin/settings.py:9`
- `DEBUG_TOOLBAR = int(os.environ.get("DEBUG_TOOLBAR", 0)) and 'test' not in sys.argv`. `sys` is already imported. This covers `settings.py:379` and `urls.py:102`

### B — Bump django-debug-toolbar
**File**: `requirements-dev.txt`: `django-debug-toolbar==4.3.0` → latest `5.2.x`
- Check the 5.x changelog for config changes (`SHOW_TOOLBAR_CALLBACK` still accepted; the `debug_toolbar.urls` include is unchanged)
- Check manually that the toolbar renders with `DEBUG_TOOLBAR=1` via `make dev_up`

### C — Bump django-tastypie
**File**: `requirements.txt`: `django-tastypie==0.14.7` → `0.15.1`
- Review the 0.15.0/0.15.1 changelogs for behavior changes that affect `src/api/` (custom `api/tastypie_custom.py`, JSONField `isinstance` check, serializers)
- Run `make dev_test_app app=api` (or equivalent), then the full suite

### D — Pin setuptools
**File**: `Dockerfile:24`: `pip install --upgrade pip "setuptools<81"`
- Add a comment on the line: deform 3.0.1 imports `pkg_resources`, which setuptools 81 removes

### E — POST logout
**File**: `src/templates/menu.html:130`
- Replace `<li><a href="{% url 'auth_logout' %}" title="Logout">…</a></li>` with a `<form method="post" action="{% url 'auth_logout' %}">{% csrf_token %}<button type="submit" class="btn-link" title="Logout">{% trans 'Logout' %}</button></form>` inside the `<li>`. Style it to look like the other dropdown items (Bootstrap 2 dropdown: inline CSS or a small class, no extra JS)
- Leave `biremelogin/urls.py` unchanged (`LogoutView` accepts POST on 4.2 and 5.2)
- Check that `authentication/logout.html` and `next_page='/'` still behave as before
- **Test** (in `main/tests.py` or a new `biremelogin/tests.py`): log in, `POST reverse('auth_logout')`, assert a redirect to `/` and that the session is anonymous. Optionally assert that the rendered menu contains a `<form` with the logout action

### F — Aware datetimes in biblioref tests
**File**: `src/biblioref/tests.py` (lines ~428–524)
- Replace `created_time="1970-01-01 00:00"` with an aware value, e.g. a module-level `EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)` (`datetime.timezone`, not the removed `django.utils.timezone.utc`)

### G — Order institution list
**File**: `src/institution/views.py` `InstGenericListView.get_queryset()`
- In the `filter(cc_code=user_cc)` branch, add `.order_by('-id')`. This matches the default ordering of the other branch. This branch usually returns only the user's own institution(s), so the visible impact is minimal

### H — Verify and document
- `make dev_build && make dev_up`
- `make dev_test_deprecations app="main events multimedia biblioref leisref institution oer title thesaurus suggest classification error_reporting api"`: zero `RemovedInDjango` lines
- `make dev_test`: all green
- Update plan `001`, write the log in `.ai/logs/`

## Implementation Order

1. A (toolbar off in tests), then run the suite to confirm the form `default.html` warning is gone
2. F, G (test/app-only fixes; no rebuild needed)
3. E (logout + test)
4. D, B, C (requirement/Docker changes), then `make dev_build && make dev_up`. Bump tastypie last so any API regression is isolated
5. H

## Out of Scope

- The Django 5.2 bump itself and the Python 3.13/3.14 image (plan 5.2–5.4)
- `RemovedInDjango60Warning` items that only appear once running on 5.x (e.g. `FORMS_URLFIELD_ASSUME_HTTPS`). These are handled in plan 5.6
- Replacing `deform` or patching its `pkg_resources` use
- Switching away from `MD5PasswordHasher`
