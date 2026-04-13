# Add indexed_database filter to LeisRef API

## Summary

Added `indexed_database` filtering support to the Legislation (LeisRef) API endpoint, allowing filtering of legislation records by database acronym.

## Changes

### `src/api/legislation.py`
- Imported `Database` from `leisref.models` (the Act model's M2M points to `leisref.Database`, not `database.Database`)
- Added `'indexed_database': ALL` to `Meta.filtering`
- Added `indexed_database` handling in `build_filters()` — looks up `Database` by acronym and filters the queryset

### `src/api/tests.py`
- Added `test_filter_by_indexed_database` to `LeisrefApiTests` — verifies that `?indexed_database=LILACS` returns only acts indexed in that database

## Usage

```
GET /api/leisref/?indexed_database=LILACS
```

## Notes

- Pattern follows `ReferenceResource` in `bibliographic.py`
- Key discovery: `Act.indexed_database` is a M2M to `leisref.Database`, not `database.Database` — they are separate models with the same class name
