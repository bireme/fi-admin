# Plan: Phase 1.4 — Tastypie API Endpoint Tests

## Context

Item 1.4 of `.ai/plans/001-upgrade-django-to-5.2.md` calls for API endpoint tests as part of the regression safety net needed before the Django 2.2 → 5.2 upgrade. The fi-admin project currently has **no tests for its Tastypie API** (`src/api/` has 26 modules but no `tests.py`). Since the upgrade will touch Django, Tastypie, and serializers, an API test suite is critical to catch regressions — especially because `django-tastypie` compatibility with Django 5.x is flagged as a HIGH risk in the plan's Risk Registry.

Goal: create `src/api/tests.py` with GET list + GET detail smoke tests for the 8 main Tastypie resources listed in the plan.

## Scope

Resources to cover (all exposed under `/api/` prefix, registered in `src/api/urls.py`):

| Resource | Endpoint | Class | File |
|---|---|---|---|
| bibliographic | `/api/bibliographic/` | `ReferenceResource` | `src/api/bibliographic.py:29` |
| event | `/api/event/` | `EventResource` | `src/api/events_api.py:17` |
| multimedia | `/api/multimedia/` | `MediaResource` | `src/api/multimedia_api.py:19` |
| oer | `/api/oer/` | `OERResource` (ApiKeyAuthentication) | `src/api/oer_api.py:21` |
| leisref | `/api/leisref/` | `LeisrefResource` | `src/api/legislation.py:21` |
| title | `/api/title/` | `TitleResource` | `src/api/title_api.py:50` |
| institution | `/api/institution/` | `InstitutionResource` | `src/api/institution_api.py:25` |
| classification | `/api/classification/`, `/api/community/`, `/api/collection/` | classification resources | `src/api/classification_api.py` |

## Approach

Create a single `src/api/tests.py` module extending `BaseTestCase` from `src/utils/tests.py:13`, mirroring the patterns already used in `biblioref/tests.py`, `events/tests.py`, `multimedia/tests.py`, `leisref/tests.py`, `oer/tests.py`, `title/tests.py`.

### Structure

```
src/api/tests.py
├── ApiTestBase(BaseTestCase)        # shared setup: create sample objects via model_bakery
├── BibliographicApiTests
├── EventApiTests
├── MultimediaApiTests
├── OerApiTests                      # uses ApiKey (see below)
├── LeisrefApiTests
├── TitleApiTests
├── InstitutionApiTests
├── ClassificationApiTests           # community + collection + classification
└── ThesaurusApiTests                # desc, qualif, ths (simple GET smoke)
```

Each resource test class covers:
1. **GET list returns 200** and JSON payload with `meta` + `objects` keys (Tastypie envelope).
2. **GET detail returns 200** for a known object (`/api/<resource>/<pk>/`) and `404` for a missing pk.
3. **Response format** is JSON and `objects` count matches created fixtures.
4. **Unsupported method returns 405** (e.g., `POST` to read-only resources) — one per class is enough.

### OER specifics

`OERResource` uses `ApiKeyAuthentication`. Create a user + `tastypie.models.ApiKey` in `setUp`, then pass `?username=...&api_key=...` query params (Tastypie's default) on all OER requests. Verify that a request without credentials returns `401`.

### Fixture creation

Use `model_bakery.baker.make(...)` for each resource's underlying model. Follow the field-filling pattern in `biblioref/tests.py` / `multimedia/tests.py`. Where a model requires related descriptor/thematic/keyword inlines for visibility, create the minimum set; where the API filters by `status` (e.g., published), set it explicitly.

### Reused utilities

- `BaseTestCase` (`src/utils/tests.py:13`) — provides `self.client`, `login_*` helpers, user/profile setup.
- `model_bakery.baker` — already used across the repo per Phase 1.2.
- `django.test.Client` with `content_type='application/json'` for Tastypie requests.
- `reverse()` is not used by Tastypie URL names; use hardcoded URL strings under `/api/...` (consistent with the plan's intent and Tastypie convention).

## Files to create / modify

- **Create**: `src/api/tests.py` — all API test classes.
- **Modify**: `bireme/run_tests.sh` — ensure `api` is in the list of apps executed (Phase 1.1 already widens this; confirm `api` is included).
- **No production code changes**.

## Verification

1. `make dev_test_app app=api` — all new tests pass.
2. `make dev_test` (full suite) — no regressions.
3. `make dev_coverage` — confirm `src/api/*.py` coverage increases from ~0%.
4. Manually hit one endpoint in a running container (`curl http://localhost:8000/api/event/?format=json`) to confirm the tests mirror real behavior.
5. Check that OER auth test actually rejects unauthenticated requests (sanity: temporarily remove the api_key param and confirm 401).

### Thesaurus API specifics

Although not listed in plan item 1.4, add a lightweight `ThesaurusApiTests` class covering the JSON endpoints wired in `src/api/urls.py:73-75`:

- `GET /api/desc/` → `ThesaurusAPIDescResource` (`src/api/thesaurus_api_desc.py`)
- `GET /api/qualif/` → `ThesaurusAPIQualifResource` (`src/api/thesaurus_api_qualif.py`)
- `GET /api/ths/` → `ThesaurusAPITreeNumberResource` (`src/api/thesaurus_treenumber_api.py`)

For each: create a minimal fixture via `baker.make` on the underlying thesaurus model, hit the list endpoint, assert 200 and JSON envelope. Skip the ID-format renderers (`/api/descriptors/`, `/api/qualifiers/`) and the solr-index variants — they are rendering helpers, not data APIs.

## Out of scope

- Custom `prepend_urls` endpoints (`get_search`, `get_last_id`, `get_next`) — these call external search services and belong to a later, richer test pass.
- POST/PUT/DELETE semantics beyond the single OER auth check.
- Schema (`/api/<resource>/schema/`) tests.
