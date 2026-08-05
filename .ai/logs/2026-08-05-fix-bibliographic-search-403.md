# Fix: bibliographic search endpoint returning no results (403 from search service)

## Symptom

`GET /api/bibliographic/search/` returned an empty/error payload instead of search
results. The failure was silent — no error surfaced to the caller.

## Root cause

The upstream search service (`SEARCH_SERVICE_URL`, nginx-fronted) rejects the request
with **403 Forbidden** unless both of these are sent:

1. `Content-Type: application/json` — the code called
   `requests.post(..., data=search_params_json)` with a `str` body, so `requests` sent
   **no** `Content-Type` header at all.
2. A non-default `User-Agent` — the code set no UA, so `requests` sent its default
   `python-requests/2.34.2`, which the service's nginx blocklists (as it does `curl/*`).

Verified against `https://iahx-api.teste.bvsalud.org/search_json` from the dev
container, 3 runs per case:

| Headers | Result |
| --- | --- |
| apikey only (default UA, no CT) | 403 |
| apikey + `Content-Type: application/json` | 403 |
| apikey + `User-Agent: fi-admin` | 403 |
| apikey + CT + UA | **200** |
| CT + UA, no apikey | 422 (app-level, past nginx) |

The 403 body is HTML, so `r.json()` raised `ValueError` and the handler fell back to a
generic `{"type": "error", "message": "invalid output"}` — which is why the failure was
invisible. There was no status-code check and no logging.

## Changes — `src/api/bibliographic.py` (`ReferenceResource.get_search`)

- Added `Content-Type: application/json` and `User-Agent: fi-admin` to
  `request_headers`, with a comment explaining why the service needs them.
- Included the HTTP status code in the fallback error message so a future failure is
  diagnosable instead of silent.
- Guarded the `id=` compatibility block with `'diaServerResponse' in response_json`.
  On the error path `response_json` is a truthy dict without that key, so the existing
  `if id != '' and response_json:` raised `KeyError` → 500 instead of returning the
  error payload.

## Verification

- `GET /api/bibliographic/search/?q=malaria&count=3` → HTTP 200, `numFound=3745`, 3 docs.
- `GET /api/bibliographic/search/?id=biblioref.referencesource.1701452` → HTTP 200,
  `match` element present, `numFound=1`.
- `make dev_test_app app=api` → 36 tests, OK.

## Rollout to the rest of `src/api/`

A full sweep found **16** call sites to `search_json` across 13 files (more than the 9
first estimated). The same header fix was applied to all 15 remaining sites:

`events_api.py` (×2), `institution_api.py`, `legislation.py`, `lis_old_api.py`,
`multimedia_api.py`, `oer_api.py`, `resources_api.py`, `thesaurus_api.py` (×2),
`thesaurus_api_desc.py`, `thesaurus_api_qualif.py`, `thesaurus_solr_api.py` (×2),
`title_api.py`.

Two further defects were found and fixed during that sweep:

1. **The error fallback was discarded.** 9 sites built `response_json` in a
   `try/except ValueError`, then returned `self.create_response(request, r.json())` —
   re-parsing the body and re-raising the same `ValueError` as a 500. The handler was
   dead code. Now returns `response_json`.
   (`institution_api`, `oer_api`, `thesaurus_api` ×2, `thesaurus_api_desc`,
   `thesaurus_api_qualif`, `thesaurus_solr_api` ×2, `title_api`)
2. **`KeyError` on the `id=` path** — the `'diaServerResponse' in response_json` guard
   was applied at 5 more sites (`legislation`, `multimedia_api`, `oer_api`,
   `resources_api`, `events_api`).

`title_api.py` had no error handling at all; the standard `try/except` was added.

### Verification

All 14 routed search endpoints return HTTP 200 with results:

| Endpoint | numFound |
| --- | --- |
| `/api/bibliographic/search/` | 741730 |
| `/api/resource/search/` | 20859 |
| `/api/event/search/` | 7266 |
| `/api/event/next/` | 200 OK |
| `/api/multimedia/search/` | 12320 |
| `/api/title/search/` | 1217 |
| `/api/leisref/search/` | 41299 |
| `/api/oer/search/` | 1614 |
| `/api/institution/search/` | 391 |
| `/api/descriptors/thesaurus/search/` | 2 |
| `/api/qualifiers/thesaurus/search/` | 2 |
| `/api/desc/thesaurus/search/` | 4610 |
| `/api/qualif/thesaurus/search/` | 2 |
| `/api/desc/index/thesaurus/search/` | 2 |
| `/api/qualif/index/thesaurus/search/` | 2 |

- `python -m compileall /app/api` → clean.
- `make dev_test` → 201 tests across 13 apps, all OK.

### Notes

- `lis_old_api.search` was patched for consistency but could not be exercised: its route
  is commented out in `api/urls.py:64`, so it is dead code.

## Consolidation — `api/search_service.py`

The headers had been duplicated at 16 sites. Extracted a shared client so the URL,
apikey, headers and error handling live in one place:

- `get_search_headers()` — builds the headers, reading settings at call time.
- `search_service_request(search_params)` — POSTs and decodes, returning the error dict
  with the HTTP status on a non-JSON body.
- `duplicate_response_to_match(response_json)` — the `id=` compatibility copy, a no-op
  on error payloads.

All 16 call sites across 13 modules now call the helper; the per-site `search_url`,
`request_headers`, `search_params_json` and `requests.post` were removed, along with the
`requests`/`json` imports left unused.

## Tests — `api/tests.py`

Added `SearchServiceTests` (8) and `SearchEndpointTests` (7, most parameterised over all
15 routed endpoints via `subTest`), with `requests.post` mocked. They cover the required
headers, the JSON body encoding, the 403/non-JSON fallback, the `id=` match duplication
and the facet forwarding.

Each was checked against a deliberately reintroduced bug — the tests fail as intended:

| Mutation | Failures |
| --- | --- |
| `User-Agent` header removed | 16 |
| `Content-Type` header removed | 18 |
| `diaServerResponse` guard removed | 8 |
| HTTP status dropped from the error message | 17 |
| `if id != '':` condition dropped | 1 |

### Verification after consolidation

- `make dev_test` → 218 tests across 13 apps, all OK (api app: 36 → 53).
- All 15 routed endpoints re-checked live against the real service, all HTTP 200 with
  results.
