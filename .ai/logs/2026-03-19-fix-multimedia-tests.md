# Fix multimedia app unit tests

## Date: 2026-03-19

## Summary

Fixed 2 failing tests in the multimedia app (`test_add_media` and `test_edit_media`).

## Causes

1. Missing AttachmentFormSet management form data in test minimal_form_data() — added
  attachments-attachment-content_type-object_id-TOTAL_FORMS/INITIAL_FORMS fields.
  2. JSONField crash on None — added 'description_translations': 'null' to the test form data so json.loads() doesn't receive None
  during form re-rendering.
  3. Missing formset validation in multimedia/forms.py — the DescriptorFormSet used BaseDescriptorInlineFormSet (no minimum count check)
   instead of DescriptorRequired, and ResourceThematicFormSet lacked ResourceThematicRequired. Fixed both to match the pattern used by
  events and main apps.
  4. test_edit_media logic — restructured to use minimal_form_data() (no descriptors) for the status=1 rejection test, and
  complete_form_data() for the valid submission test.

## Changes

### `bireme/multimedia/tests.py`
- Added missing `attachments-attachment-content_type-object_id` management form fields to `minimal_form_data()` — the view's `form_valid` instantiates an `AttachmentFormSet` which requires these fields.
- Added `description_translations: 'null'` to `minimal_form_data()` — the `JSONField` form field's `bound_data` method calls `json.loads(data)` and crashes when data is `None`.
- Fixed `test_edit_media` to use `minimal_form_data()` (no descriptors/thematics) for the status=1 validation check, and `complete_form_data()` for the valid submission — previously both used `complete_form_data` with status toggled, but valid descriptors/thematics caused the publication validation to pass unexpectedly.

### `bireme/multimedia/forms.py`
- Changed `DescriptorFormSet` to use `DescriptorRequired` base class instead of `BaseDescriptorInlineFormSet` — this adds the "at least one descriptor" validation that the tests expect (consistent with `events` and `main` apps).
- Changed `ResourceThematicFormSet` to use `ResourceThematicRequired` base class — adds the "at least one thematic area" validation (consistent with other apps).
- Updated import to match: `DescriptorRequired` instead of `BaseDescriptorInlineFormSet`.

### `Makefile`
- Added `-T` flag to `dev_test_app` target's `docker-compose exec` command to support non-TTY execution.
