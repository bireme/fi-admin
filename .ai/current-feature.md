# Current Feature

Add `indexed_database` filter to Legislation (LeisRef) API

## Status

Completed

## Goals

- Add `indexed_database` filtering support to `LeisrefResource` in `src/api/legislation.py`
- Follow the same pattern used in `ReferenceResource` in `src/api/bibliographic.py` (lines 52-55)
- Allow filtering legislation records by database acronym via the API query parameter `indexed_database`

## Notes

- **Reference implementation**: `src/api/bibliographic.py` lines 37-44 (Meta filtering) and 52-55 (`build_filters` method)
- In `bibliographic.py`, the filter looks up a `Database` object by acronym and filters the queryset by `indexed_database__exact`
- Need to verify that the `Act` model in `leisref` has an `indexed_database` field/relationship
- Uses `database.models.Database` for the acronym-to-id lookup

## Detailed plan

<!-- Add reference to the detailed plan file here, if applicable -->

## History

- 2026-04-13: Starting Add `indexed_database` filter to Legislation (LeisRef) API

