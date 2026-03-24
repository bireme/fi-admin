# Plan: Create CRUD unit tests for title app

## Context

The `src/title/tests.py` file does not exist yet. Following the pattern used in `src/oer/tests.py` and `src/leisref/tests.py`, we need CRUD tests for the Title (serial titles/journals) app.

**Key differences from OER/leisref:**

1. **10 formsets** (vs 5 in OER): Issues, OnlineResources, BVSSpecialty, TitleVariance, IndexRange, Audit, Collection, Descriptor, Keyword, PublicInfo
2. **Descriptor is required** — uses `DescriptorRequired` formset that enforces at least 1 descriptor. So even `minimal_form_data` needs a descriptor entry.
3. **Status is CharField** ('C'/'D'/'?') not integer — `is_valid_for_publication` checks `status == 1` which never matches, so no publication validation applies.
4. **`action` POST field required** — `form_valid` reads `self.request.POST['action']`; must be `'save'` (not 'preview'/'edit') to actually save and redirect.
5. **M2M country field** (blank=False) — must be submitted as `country` in POST data after save via `form.save_m2m()`.
6. **No owner filtering** — list view's `filter_owner` code is commented out; all titles visible to all users.
7. **Delete restricted to BR1.1** — `TitleDeleteView.get_object()` checks `user_cc == "BR1.1"` (not just same CC).
8. **Deletes Descriptor + Keyword** (not ResourceThematic like OER).
9. **`login_admin()` lacks `{"Title": "admin"}`** — but superuser access still works; form `__init__` handles `None` role fine.
10. **List template link format**: `<a href="/title/edit/{id}">{id_number}</a>` — shows `id_number` not `id`.
11. **No `ResourceThematic` in title** — uses `Keyword` generic inline instead.

**URL prefix:** `/title/` (from `src/fi-admin/urls.py`).

## File to create

- `src/title/tests.py`

## Reference files

- `src/oer/tests.py` — latest test pattern to mirror
- `src/leisref/tests.py` — test pattern reference
- `src/title/models.py` — Title, OnlineResources, TitleVariance, BVSSpecialty, IndexRange, Audit, Issue, Collection, PublicInfo
- `src/title/forms.py` — TitleForm, 10 formsets, DescriptorRequired validation
- `src/title/views.py` — TitleListView, TitleCreateView, TitleUpdateView, TitleDeleteView; `action` POST field
- `src/title/urls.py` — URL routes
- `src/utils/tests.py` — BaseTestCase helpers
- `src/utils/models.py` — Country model (code, name)

## Test structure

### 1. Helper functions

**`minimal_form_data(country_id)`** — Minimum fields to submit the Title form:
- `status`: 'C' (Current)
- `title`: test title
- `shortened_title`: test shortened title
- `creation_date`: '20200101'
- `initial_date`: '2020' (required when status='C')
- `country`: str(country_id) — M2M
- `action`: 'save' — required by form_valid
- Descriptor formset with 1 entry (required by DescriptorRequired):
  - `main-descriptor-content_type-object_id-TOTAL_FORMS`: '1'
  - `main-descriptor-content_type-object_id-0-text`: 'malaria'
  - `main-descriptor-content_type-object_id-0-code`: '^d8462'
  - `main-descriptor-content_type-object_id-0-status`: '0'
- All other formsets with TOTAL_FORMS/INITIAL_FORMS = '0':
  - `main-keyword-content_type-object_id-*` (Keyword, generic inline)
  - `onlineresources_set-*` (OnlineResources, regular inline)
  - `titlevariance_set-*` (TitleVariance, regular inline)
  - `bvsspecialty_set-*` (BVSSpecialty, regular inline)
  - `indexrange_set-*` (IndexRange, regular inline)
  - `audit_set-*` (Audit, regular inline)
  - `issue_set-*` (Issue, regular inline)
  - `collection_set-*` (Collection, regular inline)
  - `publicinfo_set-*` (PublicInfo, regular inline)

**`create_title_object(user, country)`** — Creates Title objects via ORM:
- Creates a second user (user2) from different cooperative center
- Creates Title with required fields (`id_number`, `status`, `title`, `shortened_title`, `creation_date`, `cooperative_center_code='BR1.1'`, `created_by=user`)
- Sets M2M country after save
- Creates related Descriptor via ContentType
- Creates a second Title by user2 with `cooperative_center_code='PY3.1'`
- Returns tuple (title1, title2)

### 2. Test classes

#### `TitleTest(BaseTestCase)` — Main Title CRUD tests

**`setUp`**: Create auxiliary records:
- `Country` (required M2M for Title)

**`test_list_title`**:
- Login as admin, create title objects
- GET `/title/`
- Assert both titles are visible (no owner filtering — commented out in view)

**`test_add_title`**:
- Login as admin
- POST `/title/new` with `minimal_form_data`
- Assert redirect to `/title/`
- Assert new title appears in list
- Verify `cooperative_center_code` set correctly from user profile

**`test_edit_title`**:
- Login as admin, create title objects
- GET `/title/edit/{id}` — assert form contains title
- POST with `minimal_form_data` + updated title
- Assert redirect and updated title appears

**`test_delete_title`**:
- Login as admin (BR1.1), create title objects
- GET `/title/delete/{id}` — assert confirmation message ("Você tem certeza que deseja apagar?")
- POST `/title/delete/{id}` — assert title and related Descriptor/Keyword deleted (count == 0)
- Assert redirect to `/title/`

#### `TitleSearchTest(BaseTestCase)` — Search by ID number

**`test_search_id`**:
- Use `baker.make(Title)` to create multiple Title records with known id_numbers
- GET `/title/?id={id_number}`
- Assert correct title shown, others not shown

## Verification

```bash
make dev_test_app app=title
```
