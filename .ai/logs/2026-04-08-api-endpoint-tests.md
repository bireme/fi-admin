# 2026-04-08 — Tastypie API endpoint tests (Phase 1.4)

Implements `.ai/plans/015-api-endpoint-tests.md` — smoke tests for the
Tastypie API as part of the regression safety net for the Django 2.2 →
5.2 upgrade (`.ai/plans/001-upgrade-django-to-5.2.md` item 1.4).

## Changes

- **Created** `src/api/tests.py` — 26 tests across 9 test classes:
  - `BibliographicApiTests` — empty list + 405 POST (complex dehydrate skipped)
  - `EventApiTests` — list, detail, 404, 405 POST
  - `MultimediaApiTests` — list, detail, 405 POST
  - `OerApiTests` — public GET, 401 on unauthenticated POST, ApiKey POST passes the auth gate
  - `LeisrefApiTests` — list, detail, 405 POST
  - `TitleApiTests` — list, 405 POST
  - `InstitutionApiTests` — list, 405 POST
  - `ClassificationApiTests` — community, collection, classification lists + 405 POST
  - `ThesaurusApiTests` — `/api/desc/`, `/api/qualif/`, `/api/ths/` URL dispatch smoke
- **Modified** `src/run_tests.sh` — added `api` to the APPS list.

## Scope

- Covers standard Tastypie list + detail dispatch, JSON envelope
  (`meta`/`objects`), method restrictions, and OER's `ApiKeyAuthentication`
  behavior on POST.
- Does **not** cover custom `prepend_urls` endpoints (`get_search`,
  `get_next`, `get_last_id`) — they call external search services.
- Does **not** exercise the full dehydrate of `ReferenceResource`; the
  biblioref-specific test suite owns that coverage.
- Thesaurus tests hit the endpoints without creating fixtures because
  the underlying resources read from the `decs_portal` external DB.

## Verification

```
make dev_test_app app=api
# Ran 26 tests in 1.218s — OK
```
