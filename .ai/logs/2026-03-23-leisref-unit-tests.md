# LeisRef Unit Tests

## Date: 2026-03-23

## Summary

Created comprehensive unit tests for the `leisref` app in `src/leisref/tests.py`, following patterns established in `src/multimedia/tests.py`.

## Tests implemented (7 total)

### LeisRefTest (5 tests)
- **test_list_act** - Verifies act listing, including CC-based filtering (own acts visible, other CCs hidden)
- **test_add_act** - Tests act creation via POST with complete form data, verifies redirect and cooperative_center_code assignment
- **test_edit_act** - Tests editing an existing act, verifies form pre-population and successful update
- **test_delete_act** - Tests delete confirmation page and cascading deletion of related objects (Descriptor, ResourceThematic)
- **test_list_act_type** - Tests listing auxiliary ActType model with search
- **test_add_act_type** - Tests creating a new ActType via form POST

### LeisRefSearchTest (1 test)
- **test_search_id** - Tests search by ID (`s=id:N`) returns correct act and excludes others

## Key findings during implementation

1. **No `is_valid_for_publication` in leisref** - Unlike multimedia, leisref views don't validate descriptor/thematic requirements server-side for Published status. The edit test was adjusted to not expect this validation error.
2. **Admin login required** - The `login_editor()` helper doesn't include a LeisRef service role, so all tests use `login_admin()` which has `{"LeisRef": "admin"}`.
3. **ActType list uses `name__exact`** - The `LeisRefGenericListView` uses `__exact` (not `__icontains` like multimedia), so empty search returns nothing. The test passes a search parameter instead of relying on empty listing.
4. **Form choice validation** - `ActForm.__init__` sets empty choices for `act_type` on create (no instance.id), but `ModelChoiceField` validates against queryset, not choices, so POST works correctly.

## Helper functions created
- `minimal_form_data(scope_region_id, act_type_id)` - Minimum fields + all formset management forms
- `complete_form_data(scope_region_id, act_type_id, thematic_area_id)` - Adds descriptor and thematic area entries
- `create_act_object(user, scope_region, act_type, thematic_area)` - Creates two Act objects (different CCs) with related records via ORM
