# Analyze migrations generated after Django 4.2 upgrade

## Context
`make dev_makemigrations` generated 10 new migration files (attachments, biblioref,
classification, database, help, institution, oer, related, thesaurus, title), all
composed only of `AlterField` operations.

## Analysis
Ran `sqlmigrate` for each new migration against the dev MySQL 8 database.
**Every operation renders as `-- (no-op)`** — none of them produce DDL.

The diffs are model-state only:
- `verbose_name` label changes (e.g. `Pages` -> `Page identifier`, `Clinical trial registry name` -> `Clinical trial registry`, `Language used for description` -> `Language`).
- `choices` list changes (language lists, `institution.status`, `contact.prefix`, `url.url_type`, `help.source`). Choices are never stored in the DB schema.
- Dropped defaults / `bytes` choice keys left over from Python 2 (`attachments.language`).
- Explicit `on_delete` on ForeignKeys and `related_name`/`to` casing normalization on `title.users` M2M.
- `upload_to` callable reference on `publicinfo.logo_image_file`.

## Changes
- `Makefile`: added `dev_sqlmigrate` target (`make dev_sqlmigrate app=<app> migration=<number>`).

## Conclusion
Safe to commit and apply: the migrations only sync Django's migration state with the
current models; applying them writes rows to `django_migrations` and touches no table.
