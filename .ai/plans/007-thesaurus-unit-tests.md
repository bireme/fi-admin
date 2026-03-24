# Plan: Create CRUD unit tests for thesaurus app

## Context

The `src/thesaurus/tests.py` contains only the default Django stub. Following the pattern used in `src/oer/tests.py` and `src/title/tests.py`, we need CRUD tests for the Thesaurus app (Descriptors and Qualifiers).

**Key differences from OER/Title:**

1. **Multi-step creation flow** — DescCreateView (Step 1) creates `IdentifierDesc` + formsets, then redirects to Step 2 (concept+term creation). Unlike OER/Title which redirect to list.
2. **List view queries TermListDesc, not IdentifierDesc** — The list shows terms filtered by `choiced_thesaurus` and `visited` params.
3. **Permission model is different** — BR1.1 users get full access; others need `service_role` matching `thesaurus.thesaurus_scope`. Since `login_admin()` creates superuser with cc=BR1.1, all views are accessible.
4. **No `action` POST field** — Unlike title app.
5. **6 inline formsets for Descriptor Step 1** — DescriptionDesc, TreeNumbersListDesc, PharmacologicalActionList, SeeRelatedListDesc, PreviousIndexingListDesc, EntryCombinationListDesc.
6. **Tree number required for create** — `form_valid` requires at least one tree_number entry, and validates format (odd length, letter start, digit at position 3).
7. **code_controller** — Sequential numbering for `decs_code` and `descriptor_ui` auto-generated on create.
8. **IdentifierDescForm requires `ths` kwarg** — The `__init__` pops `ths` to filter abbreviation queryset. Passed via GET param `?ths=`.
9. **Delete confirmation text** — `"Are you sure you want to delete?"` (English, via i18n).
10. **Delete redirects to** `/thesaurus/descriptors/?ths={ths_id}`.
11. **Edit success URL** — Redirects to detail view of first term, not to list.
12. **Formset prefixes** — Django default inline prefixes (e.g., `descriptiondesc_set-*`, `treenumberslistdesc_set-*`, etc.).
13. **Qualifier structure mirrors Descriptor** — Parallel views, models, and formsets.

**URL prefix:** `/thesaurus/` (from `src/fi-admin/urls.py`).

## File to create

- `src/thesaurus/tests.py`

## Reference files

- `src/oer/tests.py` — latest test pattern to mirror
- `src/thesaurus/models_thesaurus.py` — Thesaurus, code_controller, code_controller_term
- `src/thesaurus/models_descriptors.py` — IdentifierDesc, DescriptionDesc, TreeNumbersListDesc, etc.
- `src/thesaurus/models_qualifiers.py` — IdentifierQualif, DescriptionQualif, TreeNumbersListQualif, etc.
- `src/thesaurus/forms.py` — IdentifierDescForm (requires `ths` kwarg), all formsets
- `src/thesaurus/views.py` — DescListView, DescCreateView, DescRegisterUpdateView, DescDeleteView + Qualifier equivalents
- `src/thesaurus/urls.py` — URL routes
- `src/utils/tests.py` — BaseTestCase helpers
- `src/templates/thesaurus/thesaurus_home.html` — list template (shows `term_string (language_code)`)
- `src/templates/thesaurus/descriptor_confirm_delete.html` — delete confirmation ("Are you sure you want to delete?")

## Test structure

### 1. Helper functions

**`create_thesaurus()`** — Creates a `Thesaurus` object with required fields:
- `thesaurus_name`: 'DeCS'
- `thesaurus_author`: 'BIREME'
- `thesaurus_scope`: 'DeCS'
- `thesaurus_acronym`: 'DEC'

**`minimal_form_data_descriptor(thesaurus_id)`** — Minimum fields to submit the Descriptor Step 1 form:
- `thesaurus`: str(thesaurus_id)
- DescriptionDesc formset with TOTAL_FORMS='0', INITIAL_FORMS='0' (prefix: `descriptiondesc_set`)
- TreeNumbersListDesc formset with TOTAL_FORMS='1', INITIAL_FORMS='0' + 1 valid tree_number entry (prefix: `treenumberslistdesc_set`):
  - `treenumberslistdesc_set-0-tree_number`: 'A01' (valid format: odd length, starts with letter, digit at pos 3)
- PharmacologicalActionList formset TOTAL/INITIAL='0' (prefix: `pharmacologicalactionlist_set`)
- SeeRelatedListDesc formset TOTAL/INITIAL='0' (prefix: `seerelatedlistdesc_set`)
- PreviousIndexingListDesc formset TOTAL/INITIAL='0' (prefix: `previousindexinglistdesc_set`)
- EntryCombinationListDesc formset TOTAL/INITIAL='0' (prefix: `entrycombinationlistdesc_set`)

**`create_descriptor_with_term(thesaurus, user)`** — Creates a full Descriptor+Concept+Term chain via ORM:
- Creates `IdentifierDesc` linked to thesaurus
- Creates `IdentifierConceptListDesc` linked to identifier
- Creates `TermListDesc` linked to concept, with `term_string`, `language_code='en'`, `status=1`, `concept_preferred_term='Y'`, `record_preferred_term='Y'`, `term_thesaurus=str(thesaurus.id)`
- Returns (identifier, concept, term)

**`minimal_form_data_qualifier(thesaurus_id)`** — Similar to descriptor but for Qualifier Step 1:
- `thesaurus`: str(thesaurus_id)
- `abbreviation`: valid abbreviation (required, max 4 chars)
- DescriptionQualif formset TOTAL/INITIAL='0' (prefix: `descriptionqualif_set`)
- TreeNumbersListQualif formset with 1 valid tree_number entry (prefix: `treenumberslistqualif_set`)

**`create_qualifier_with_term(thesaurus, user)`** — Creates Qualifier+Concept+Term chain via ORM.

### 2. Test classes

#### `DescriptorTest(BaseTestCase)` — Descriptor CRUD tests

**`setUp`**: Create auxiliary records:
- `Thesaurus` (required FK for IdentifierDesc)

**`test_list_descriptor`**:
- Login as admin, create descriptor with term via ORM
- GET `/thesaurus/descriptors/?choiced_thesaurus={ths_id}&visited=ok`
- Assert `term_string` appears in response (list shows TermListDesc objects)

**`test_add_descriptor`**:
- Login as admin
- POST `/thesaurus/descriptors/new?ths={ths_id}&language_code=en&term=test` with `minimal_form_data_descriptor`
- Assert redirect to `/thesaurus/descriptors/register/term` (Step 2 — concept+term creation)
- Assert `IdentifierDesc` object was created with auto-generated `decs_code` and `descriptor_ui`

**`test_edit_descriptor`**:
- Login as admin, create descriptor with term via ORM
- GET `/thesaurus/descriptors/register/edit/{id}?ths={ths_id}` — assert form loads
- POST with form data + updated fields
- Assert redirect to detail view

**`test_delete_descriptor`**:
- Login as admin, create descriptor with term via ORM
- GET `/thesaurus/descriptors/delete/{id}?ths={ths_id}` — assert "Are you sure you want to delete?"
- POST — assert IdentifierDesc deleted (count == 0)
- Assert redirect to `/thesaurus/descriptors/?ths={ths_id}`

#### `QualifierTest(BaseTestCase)` — Qualifier CRUD tests

Mirror of DescriptorTest but for Qualifier models and URLs:
- URLs at `/thesaurus/qualifiers/...`
- Uses `IdentifierQualif`, `IdentifierConceptListQualif`, `TermListQualif`

**`test_list_qualifier`**, **`test_add_qualifier`**, **`test_edit_qualifier`**, **`test_delete_qualifier`**

#### `DescriptorSearchTest(BaseTestCase)` — Search descriptors

**`test_search_term`**:
- Create multiple descriptors with terms via ORM
- GET `/thesaurus/descriptors/?choiced_thesaurus={ths_id}&visited=ok&s={term_string}`
- Assert correct term shown, others not shown

## Verification

```bash
make dev_test_app app=thesaurus
```
