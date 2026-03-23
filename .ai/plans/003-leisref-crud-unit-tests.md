# Plan: Create unit tests for leisref app

## Context

The `src/leisref/tests.py` file is nearly empty (just imports and a bare `setUp`). The `src/multimedia/tests.py` has comprehensive CRUD tests that serve as a proven pattern. The goal is to create analogous tests for the leisref app covering Act CRUD operations, auxiliary model CRUD, search by ID, and permission checks.

**Key difference from multimedia:** The `login_editor()` helper does NOT have a `LeisRef` service role, so editor-level tests will need `login_admin()` (which has `{"LeisRef": "admin"}`). The leisref views check `user_data['service_role'].get('LeisRef')` for permissions.

**URL prefix:** leisref is mounted at `/legislation/` (from `src/fi-admin/urls.py`).

## Files to modify

- `src/leisref/tests.py` — the only file to edit

## Files to reference

- `src/multimedia/tests.py` — test patterns to mirror
- `src/leisref/models.py` — Act, ActType, ActCountryRegion, ActURL, ActRelationship, and other models
- `src/leisref/forms.py` — ActForm fields, formsets (DescriptorFormSet, URLFormSet, AttachmentFormSet, RelationFormSet, ResourceThematicFormSet)
- `src/leisref/views.py` — view permission logic, delete cascading behavior
- `src/leisref/urls.py` — URL routes
- `src/utils/tests.py` — BaseTestCase helpers
- `src/templates/leisref/act_confirm_delete.html` — delete confirmation message

## Test structure

### 1. Helper functions

**`minimal_form_data()`** — Minimum fields to submit the Act form:
- `status`: '0' (Draft)
- `scope_region`: FK id (created in setUp)
- `act_type`: FK id (created in setUp)
- `title`: test title
- `official_ementa_translations`: 'null'
- `unofficial_ementa_translations`: 'null'
- All formset TOTAL_FORMS/INITIAL_FORMS set to '0':
  - `main-descriptor-content_type-object_id-*` (Descriptor, generic inline)
  - `main-resourcethematic-content_type-object_id-*` (ResourceThematic, generic inline)
  - `attachments-attachment-content_type-object_id-*` (Attachment, generic inline)
  - `acturl_set-*` (ActURL, regular inline — prefix from related_name default)
  - `related-*` (ActRelationship, regular inline — prefix from related_name='related')

**`complete_form_data()`** — Adds descriptor + thematic area to minimal for valid Published submission:
- Descriptor formset with 1 entry
- ResourceThematic formset with 1 entry
- `issue_date`, `publication_date`

**`create_act_object(user)`** — Creates Act objects directly via ORM for list/edit/delete tests:
- Creates a second user (user2) from different cooperative center
- Creates Act with required FKs (scope_region, act_type)
- Creates related Descriptor and ResourceThematic via ContentType
- Creates a second Act by user2 with different cooperative center code

### 2. Test classes

#### `LeisRefTest(BaseTestCase)` — Main Act CRUD tests

**`setUp`**: Create auxiliary records needed by Act form:
- `ActCountryRegion` (required FK)
- `ActType` with scope_region relation (required FK)
- `ThematicArea` (needed for ResourceThematic)

**`test_list_act`** — Mirrors `test_list_media`:
- Login as admin, create act objects
- GET `/legislation/`
- Assert own act is visible, other CC's act is not (if restricted)

**`test_add_act`** — Mirrors `test_add_media`:
- Login as admin
- POST `/legislation/new` with complete_form_data
- Assert redirect to `/legislation/`
- Assert new act appears in list
- Assert cooperative_center_code is set correctly

**`test_edit_act`** — Mirrors `test_edit_media`:
- Login as admin, create act objects
- GET `/legislation/edit/{id}` — assert form contains act title
- POST with minimal data + status=1 (Published) — assert validation error for missing descriptor/thematic
- POST with complete data — assert redirect and success

**`test_delete_act`** — Mirrors `test_delete_media`:
- Login as admin, create act objects
- GET `/legislation/delete/{id}` — assert confirmation message
- POST `/legislation/delete/{id}` — assert act and related objects deleted
- Assert redirect to `/legislation/`

**`test_list_act_type`** — Mirrors `test_list_media_type`:
- Documentalist access → 403 (no LeisRef role)
- Admin access → sees ActType in list

**`test_add_act_type`** — Mirrors `test_add_media_type`:
- Documentalist access → 403
- Admin creates new ActType via form post

#### `LeisRefSearchTest(BaseTestCase)` — Search by ID

**`test_search_id`** — Mirrors `MultimediaSearchTest.test_search_id`:
- Create multiple Acts via baker
- Search with `s=id:N` and `filter_owner=*`
- Assert correct act shown, others not shown

## Verification

Run tests with:
```bash
make dev_test_app app=leisref
```

All tests should pass. If the Makefile command doesn't exist, check with `make -n dev_test_app app=leisref` first.
