# Plan: Create CRUD unit tests for Institution app

## Context

The `src/institution/tests.py` file is empty (just the default Django stub). Following the same pattern used in `src/oer/tests.py` and `src/leisref/tests.py`, we need comprehensive CRUD tests for the Institution app covering list, create, edit, delete, and search operations.

**Key differences from OER/leisref/title:**

1. **DirIns + advanced user required** — `InstGenericListView.dispatch()` checks `user_type == 'advanced'` AND `service_role.get('DirIns')`. The `login_admin()` helper has `DirIns: admin` in service_role but does NOT have `user_type: "advanced"` in profile data. We need to update the profile data after login to add `"user_type": "advanced"`.

2. **BR1.1 restriction for create/delete** — `InstCreateView` and `InstDeleteView` both restrict to `user_cc == 'BR1.1'` in dispatch. The admin user has cc=BR1.1 so this works.

3. **4 regular inline formsets** (no generic inlines like Descriptor/ResourceThematic):
   - `ContactFormSet` (prefix: `contact_set`)
   - `URLFormSet` (prefix: `url_set`)
   - `UnitLevelFormSet` (prefix: `unitlevel_set`)
   - `AdmFormSet` (prefix: `adm_set`, max_num=1, can_delete=False)

4. **No Descriptor/ResourceThematic formsets** — unlike OER/leisref, institution has no generic inline formsets for descriptors or thematic areas.

5. **No `action` POST field** — unlike title, no special action field is needed.

6. **cc_code is unique and required** — the only truly required field on Institution.

7. **Filter owner logic** — default filters to `cc_code=user_cc`. Only BR1.1 users with `filter_owner=*` see all institutions.

8. **Delete cascades** — explicitly deletes Contact, URL, Adm, InstitutionAdhesion before main object.

9. **List template link format**: `<a href="/institution/edit/{id}">{id}</a>` — shows institution id.

10. **Search by CC code pattern** — `re.match(r"^[A-Za-z]{2}[0-9]+", search)` triggers cc_code search; otherwise searches by name/acronym.

**URL prefix:** `/institution/` (from `src/fi-admin/urls.py`).

## File to modify

- `src/institution/tests.py` — the only file to edit

## Reference files

- `src/oer/tests.py` — latest test pattern to mirror
- `src/institution/models.py` — Institution, Contact, URL, Adm, UnitLevel, Type, Category, etc.
- `src/institution/forms.py` — InstitutionForm, ContactFormSet, URLFormSet, UnitLevelFormSet, AdmFormSet
- `src/institution/views.py` — InstListView, InstCreateView, InstUpdateView, InstDeleteView
- `src/utils/tests.py` — BaseTestCase helpers (login_admin, etc.)
- `src/utils/models.py` — Country model

## Test structure

### 1. Helper functions

**`login_admin_institution(test_case)`** — Wraps `login_admin()` and patches profile to add `user_type: "advanced"`:
- Calls `test_case.login_admin()` to get user
- Parses `user.profile.data` JSON, adds `"user_type": "advanced"`
- Saves profile back
- Clears Django cache (context_processors caches user_info)
- Returns user

**`minimal_form_data(country_id)`** — Minimum fields to submit the Institution form:
- `status`: '1' (Active)
- `cc_code`: 'BR1.1.999' (unique test code)
- `name`: 'Test Institution'
- `country`: str(country_id)
- All 4 formset management forms set to appropriate values:
  - `contact_set-TOTAL_FORMS`: '0', `contact_set-INITIAL_FORMS`: '0'
  - `url_set-TOTAL_FORMS`: '0', `url_set-INITIAL_FORMS`: '0'
  - `unitlevel_set-TOTAL_FORMS`: '0', `unitlevel_set-INITIAL_FORMS`: '0'
  - `adm_set-TOTAL_FORMS`: '1', `adm_set-INITIAL_FORMS`: '0' (max_num=1, extra=1 so form expects 1)

**`create_institution_object(user, country)`** — Creates Institution objects via ORM:
- Creates a second user (user2) from different cooperative center (PY3.1) — also needs `user_type: "advanced"` and `DirIns` role
- Creates Institution with `cc_code='TST1.1'`, `name='Test Institution BR'`, `status=1`, `country=country`, `cooperative_center_code='BR1.1'`, `created_by=user`
- Creates related Contact and URL via ORM
- Creates a second Institution by user2 with `cc_code='TST3.1'`, `cooperative_center_code='PY3.1'`
- Returns tuple (inst1, inst2)

### 2. Test classes

#### `InstitutionTest(BaseTestCase)` — Main Institution CRUD tests

**`setUp`**: Create auxiliary records:
- `Country` (required FK for Institution)

**`test_list_institution`**:
- Login as admin (with advanced user_type), create institution objects
- GET `/institution/`
- Assert own institution name is visible (filter_owner default filters to user's cc_code)
- Assert other CC's institution is not visible

**`test_list_institution_all`** (optional, BR1.1 sees all):
- Login as admin
- GET `/institution/?filter_owner=*`
- Assert both institutions are visible

**`test_add_institution`**:
- Login as admin
- POST `/institution/new` with `minimal_form_data`
- Assert redirect to `/institution/`
- Assert new institution name appears in list
- Verify `cooperative_center_code` set correctly from user profile

**`test_edit_institution`**:
- Login as admin, create institution objects
- GET `/institution/edit/{id}` — assert form contains institution name
- POST with `minimal_form_data` + updated name
- Assert redirect and updated name appears

**`test_delete_institution`**:
- Login as admin (BR1.1), create institution objects
- GET `/institution/delete/{id}` — assert confirmation message ("Are you sure you want to delete?")
- POST `/institution/delete/{id}` — assert Institution, Contact, URL, Adm all deleted (count == 0)
- Assert redirect to `/institution/`

#### `InstitutionSearchTest(BaseTestCase)` — Search by name

**`test_search_name`**:
- Login as admin, create institutions with distinct names
- GET `/institution/?s={name}&filter_owner=*`
- Assert correct institution shown, others not shown

## Verification

```bash
make dev_test_app app=institution
```

All tests should pass. If the Makefile target doesn't work, fall back to:
```bash
docker compose exec app python manage.py test institution --verbosity=2
```
