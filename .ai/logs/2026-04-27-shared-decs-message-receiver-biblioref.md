# Shared DeCS Message Receiver for Biblioref

## Summary
- Added `src/static/js/decs_message_receiver.js` to centralize DeCS `message` event handling.
- Replaced the inline receiver in `src/templates/biblioref/referenceanalytic_form.html` with `FiAdminDeCSMessages.registerDescriptorReceiver()`.
- Replaced the inline receiver in `src/templates/biblioref/referencesource_form.html` with the shared receiver and disabled AI metadata writes for that form.
- Included the new static JavaScript file in both Biblioref templates.

## Validation
- `make dev_test_app app=biblioref`
  - Ran 26 tests successfully.
  - 5 tests skipped.
