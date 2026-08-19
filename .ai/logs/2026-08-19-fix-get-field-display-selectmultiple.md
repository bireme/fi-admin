# Fix `get_field_display` crash on SelectMultiple fields (Django 3.1+)

## Problem

Rendering the Title preview page (`src/templates/title/form_preview.html`) raised an
exception in `get_field_display` (`src/utils/templatetags/app_filters.py:98`) for
ManyToMany fields shown with a `SelectMultiple` widget (`country`, `text_language`,
`abstract_language`, `users`):

```
TypeError: unhashable type: 'ModelChoiceIteratorValue'
    list += [dict(field.field.choices)[int(value)]]
```

### Root cause

Since Django 3.1, `ModelChoiceIterator` yields a `ModelChoiceIteratorValue` wrapper
instead of the raw pk as the option value. On Django 3.2 that class defines `__eq__`
but no `__hash__`, so `dict(field.field.choices)` fails outright; and even where the
dict could be built, `int(value)` would fail because the wrapper has no `__int__`.
This is a Django 2.2 -> 3.2 upgrade regression (see `.ai/plans/001-upgrade-django-to-5.2.md`).

A second, pre-existing bug lived in the same block: `field.form[field.name][0]` read
only the *first* `<option>` of the select rather than the selected ones, so the tag
displayed the wrong value even when it did not crash.

## Change

`src/utils/templatetags/app_filters.py` — the `SelectMultiple` branch now reads the
labels of the selected bound subwidgets, with no pk -> label mapping and no `int()`
conversion:

```python
elif widget == 'SelectMultiple':
    selected = [str(subwidget.data['label']) for subwidget in field.form[field.name]
                if subwidget.data.get('selected')]
    out = sep.join(selected)
```

This works for `ModelMultipleChoiceField`, plain `MultipleChoiceField` and grouped
selects (`ChoiceWidget.subwidgets` flattens optgroups), and `str()` forces lazy
translated labels. The stale commented-out `getattr(object, field.name).all()` lines
were removed — the preview renders an unsaved `form.instance`, so the M2M manager is
empty there and the bound-widget data is the correct source.

## Tests

Added `GetFieldDisplayTest` to `src/utils/tests.py` covering multiple selection,
single selection and empty selection through an actual template render of the tag.
Verified the new tests fail with the old implementation and pass with the fix.

- `make dev_test_app app=utils` — 13 tests, OK
- `make dev_test_app app=title` — 14 tests, OK
