# Fix `get_field_display` crash on SelectMultiple fields (Django 3.1+)

## Context

While previewing a Title (`src/templates/title/form_preview.html`, which calls
`{% get_field_display form.instance field ', ' %}`), the template tag
`get_field_display` in `src/utils/templatetags/app_filters.py:98` crashes on
ManyToMany fields rendered with a `SelectMultiple` widget (`country`,
`text_language`, `abstract_language`, `users` in `src/title/models.py`).

### Root cause

```python
elif widget == 'SelectMultiple':
    list = []
    obj = field.form[field.name][0]          # only the FIRST option of the select
    for value in [obj.data.get('value')]:
        list += [dict(field.field.choices)[int(value)]]
```

Since **Django 3.1**, `ModelChoiceIterator` no longer yields the raw pk as the
option value: it yields a `ModelChoiceIteratorValue` wrapper (added so widgets can
carry per-option data attributes). That object defines `__str__`, `__eq__` and
`__hash__` but **no `__int__`**, so:

- `obj.data.get('value')` is a `ModelChoiceIteratorValue` (see the traceback local
  `value = <django.forms.models.ModelChoiceIteratorValue object>`), and
  `int(value)` raises `TypeError: int() argument must be a string, a bytes-like
  object or a real number, not 'ModelChoiceIteratorValue'`.
- `dict(field.field.choices)` now has `ModelChoiceIteratorValue` keys as well, so
  the lookup was equally fragile.

This is a Django 2.2 → 3.2 upgrade regression (rc/3.2 branch, `.ai/plans/001-upgrade-django-to-5.2.md`).

### Secondary bug in the same block

`field.form[field.name][0]` takes only the *first* subwidget (the first `<option>`
of the select), not the selected ones. So even when it didn't crash it printed the
first choice of the list regardless of what the user selected. `sep.join(list)` would
also fail if a label were a lazy translation object rather than `str`.

## Fix

Rewrite the `SelectMultiple` branch in `src/utils/templatetags/app_filters.py`
(lines 94–101) to read the *selected* subwidgets instead of decoding raw values.
`BoundField.__iter__` yields `BoundWidget` objects whose `.data` dict already
contains both `label` and `selected` — no pk→label mapping, no `int()`, and it
works for `ModelMultipleChoiceField`, plain `MultipleChoiceField` and
`django-multiselectfield` alike:

```python
elif widget == 'SelectMultiple':
    selected = [str(subwidget.data['label'])
                for subwidget in field.form[field.name]
                if subwidget.data.get('selected')]
    out = sep.join(selected)
```

Notes:
- Keep using the widget/bound-field data (not `getattr(object, field.name).all()`,
  the commented-out lines 99–100): the preview page renders an **unsaved**
  `form.instance`, so the M2M manager is empty there. Delete those stale comment
  lines while touching the block.
- `str(...)` forces lazy translated labels, fixing the `sep.join` fragility.
- `ChoiceWidget.subwidgets` flattens optgroups, so grouped selects are covered.

## Verification

1. `make dev_test_app app=title` and `make dev_test_app app=utils` (create the
   target if `utils` has no tests registered) — must pass.
2. Add a regression test for the tag (new `src/utils/tests.py` or extend the
   existing test module): build a `TitleForm` bound with two `country` pks, render
   `{% get_field_display form.instance field ', ' %}` and assert both country names
   appear, comma separated.
3. Manual end-to-end: run the stack via the Makefile, log in, go to
   *Title → new/edit*, select multiple countries and languages, submit to reach the
   preview step, and confirm the preview lists exactly the selected values instead
   of raising `TypeError`.
4. Per `CLAUDE.md`, write `.ai/logs/2026-08-19-fix-get-field-display-selectmultiple.md`
   summarizing the change.
