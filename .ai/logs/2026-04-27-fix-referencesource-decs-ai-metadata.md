# Fix Reference Source DeCS AI Metadata Handling

## Summary
- Fixed `src/templates/biblioref/referencesource_form.html` so the shared DeCS message receiver writes `ai_suggestion` and `ai_model` hidden fields.
- Confirmed `DescriptorForm` already renders those fields as hidden inputs for the shared descriptor formset.
- Added a regression test in `src/biblioref/tests.py` to ensure the source template includes the shared receiver and does not disable AI metadata.

## Validation
- `make dev_test_app app=biblioref`
  - Ran 27 tests successfully.
  - 5 tests skipped.
