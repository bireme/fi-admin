# Baseline Coverage Report (Phase 1.6)

Ran full test suite with coverage on Django 2.2.24 / Python 3.7 using `make dev_test_coverage`.

**Total coverage: 55% (18276 stmts, 8308 missing)**

Also fixed `dev_test_coverage` Makefile target to use `exec -T` (non-TTY) so it runs under non-interactive shells.

## Per-app baseline coverage

| App | Coverage (approx, weighted) | Notes |
|-----|-----------------------------|-------|
| api | ~20% | Tastypie resources — smoke tests only |
| attachments | ~64% | models 68%, views 53% |
| biblioref | ~35% | tests 59%; forms 14%, views 35%, search_indexes 34% |
| biremelogin | 100% | trivial |
| classification | ~90% | models 80%, views/tests 100% |
| dashboard | 31% | views untested |
| database | ~67% | no tests |
| error_reporting | ~55% | views 22% |
| events | ~85% | views 82%, models 84%, tests 100% |
| help | ~60% | views 38% |
| institution | ~75% | views 64%, models 79%, tests 100% |
| leisref | ~70% | views 73%, models 70%, tests 100% |
| log | ~70% | views 22%, middleware 90% |
| main | ~80% | views 69%, models 82%, tests 100% |
| multimedia | ~85% | views 87%, models 87%, tests 100% |
| oer | ~80% | views 74%, models 73%, tests 100% |
| related | ~65% | views 60%, models 69% |
| reports | 13% | views untested |
| suggest | ~80% | views 73%, tests 100% |
| text_block | 63% | no tests |
| thesaurus | ~30% | views 25% (huge file), tests 100% for models |
| title | ~80% | views 81%, tests 100% |
| utils | ~55% | mixed |

## Biggest gaps (priority for future test expansion)

1. `thesaurus/views.py` — 2968 stmts, 25% (largest single file in the repo)
2. `api/*` — most Tastypie resources under 30%
3. `reports/views.py` — 13%
4. `biblioref/forms.py` — 740 stmts, 14%
5. `biblioref/cross_validation.py` — 10%

## Phase 1.6 checklist

- [x] Ran full test suite with coverage (`make dev_test_coverage`)
- [x] Documented baseline coverage percentages per app
- [x] Fixed non-TTY issue in `dev_test_coverage` Makefile target

Baseline recorded: **55% overall**. This is the regression safety net for the Django 2.2 → 5.2 upgrade.
