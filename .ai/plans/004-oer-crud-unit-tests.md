# Plan: Create CRUD unit tests for OER app

## Context

The `src/oer/tests.py` file is empty (just the default Django stub). Following the same pattern used in `src/multimedia/tests.py` and `src/leisref/tests.py`, we need comprehensive CRUD tests for the OER (Open Educational Resource) app covering list, create, edit, delete, and search-by-ID operations.

**Key difference from leisref/multimedia:** The `login_admin()` helper does NOT have an `{"OER": "..."}` service_role entry. However, since `login_admin()` creates a superuser, all views (which use `LoginRequiredView`) still allow access. The `OERForm.__init__` checks `service_role.get('OER') == 'doc'` which returns False for None, so the form works fine. The permission context flags (`user_can_edit`, `user_can_change_status`) won't be set but that doesn't block superuser CRUD.

**No auxiliary model views:** Unlike leisref (which has ActType list/add views), OER has no views for managing auxiliary models (Type, License, etc.). So no auxiliary model tests needed.

**URL prefix:** OER is mounted at `/oer/` (from `src/fi-admin/urls.py`).

## File to modify

- `src/oer/tests.py` — the only file to edit

## Reference files

- `src/leisref/tests.py` — latest test pattern to mirror
- `src/multimedia/tests.py` — original test pattern
- `src/oer/models.py` — OER, Type, License, LearningContext, SourceLanguage, OERURL, Relationship
- `src/oer/forms.py` — OERForm, formsets (DescriptorFormSet, URLFormSet, AttachmentFormSet, RelationFormSet, ResourceThematicFormSet)
- `src/oer/views.py` — OERListView, OERCreateView, OERUpdateView, OERDeleteView
- `src/utils/tests.py` — BaseTestCase helpers

## Test structure

### 1. Helper functions

**`minimal_form_data()`** — Minimum fields to submit the OER form:
- `status`: '-1' (Draft)
- `title`: test title
- `CVSP_resource`: True
- All formset management forms set to TOTAL_FORMS/INITIAL_FORMS = '0':
  - `main-descriptor-content_type-object_id-*` (Descriptor, generic inline)
  - `main-resourcethematic-content_type-object_id-*` (ResourceThematic, generic inline)
  - `attachments-attachment-content_type-object_id-*` (Attachment, generic inline)
  - `oerurl_set-*` (OERURL, regular inline — default prefix from model name lowercase + `_set`)
  - `related-*` (Relationship, regular inline — fk_name='oer_related', related_name='related')

**`complete_form_data(thematic_area_id, oer_type_id, language_id, license_id, learning_context_id)`** — Adds required-for-publication fields:
- Starts with `minimal_form_data()`
- `status`: '1' (Published)
- `learning_objectives`, `description`, `creator` (JSON), `type`, `language`, `license`, `learning_context`
- Descriptor formset with 1 entry (text='malaria', code='^d8462', status='0')
- ResourceThematic formset with 1 entry

**`create_oer_object(user, oer_type_id, language_id, license_id, learning_context_id)`** — Creates OER objects via ORM:
- Creates a second user (user2) from different cooperative center (PY3.1)
- Creates OER with required fields, `created_by=user`, `cooperative_center_code='BR1.1'`
- Creates related Descriptor and ResourceThematic via ContentType
- Creates a second OER by user2 with `cooperative_center_code='PY3.1'`
- Returns tuple (oer1, oer2)

### 2. Test classes

#### `OERTest(BaseTestCase)` — Main OER CRUD tests

**`setUp`**: Create auxiliary records needed by OER form:
- `Type` (required for publication)
- `SourceLanguage` (required for publication)
- `License` (required for publication)
- `LearningContext` (required for publication)
- `ThematicArea` (needed for ResourceThematic)

**`test_list_oer`**:
- Login as admin, create OER objects
- GET `/oer/`
- Assert own OER title is visible (contains `BR1.1` title)
- Assert other CC's OER is not visible (default filter_owner='user' restricts to created_by=user)

**`test_add_oer`**:
- Login as admin
- POST `/oer/new` with `complete_form_data`
- Assert redirect to `/oer/`
- Assert new OER title appears in list
- Verify `cooperative_center_code` set correctly from user profile

**`test_edit_oer`**:
- Login as admin, create OER objects
- GET `/oer/edit/{id}` — assert form contains OER title
- POST with `minimal_form_data` + `status=1` (Published) — assert validation error for missing required-for-publication fields
- POST with `complete_form_data` — assert redirect and success

**`test_delete_oer`**:
- Login as admin, create OER objects
- GET `/oer/delete/{id}` — assert confirmation message ("Are you sure you want to delete?")
- POST `/oer/delete/{id}` — assert OER, Descriptor, ResourceThematic all deleted (count == 0)
- Assert redirect to `/oer/`

#### `OERSearchTest(BaseTestCase)` — Search by ID

**`test_search_id`**:
- Use `baker.make(OER)` to create multiple OER records
- GET `/oer/?s=id:{id}&filter_owner=*`
- Assert correct OER shown, others not shown

## Verification

```bash
make dev_test_app app=oer
```

All tests should pass. If the Makefile target doesn't work, fall back to:
```bash
docker compose exec app python manage.py test oer --verbosity=2
```
