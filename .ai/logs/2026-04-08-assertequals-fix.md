# 2026-04-08 — Fix `assertEquals` → `assertEqual` (Phase 1.5)

Implements item 1.5 of `.ai/plans/001-upgrade-django-to-5.2.md`.
`assertEquals` is a deprecated alias in Python's `unittest` and emits
`DeprecationWarning` — removing it clears noise ahead of the Django
upgrade.

## Changes

Replaced all 14 occurrences of `self.assertEquals` with
`self.assertEqual` across 7 test files:

- `src/events/tests.py` (3)
- `src/main/tests.py` (3)
- `src/suggest/tests.py` (2)
- `src/multimedia/tests.py` (3)
- `src/title/tests.py` (1)
- `src/oer/tests.py` (1)
- `src/leisref/tests.py` (1)

The plan originally listed only 4 files; `title`, `oer`, and `leisref`
were missing. Plan updated accordingly and item 1.5 marked complete.

## Verification

```
make dev_test_app app=events      # 6 OK
make dev_test_app app=main        # 9 OK
make dev_test_app app=suggest     # 7 OK
make dev_test_app app=multimedia  # 27 OK
make dev_test_app app=title       # 14 OK
make dev_test_app app=oer         # 17 OK
make dev_test_app app=leisref     # 32 OK
```
