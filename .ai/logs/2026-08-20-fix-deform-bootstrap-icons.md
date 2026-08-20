# Fix: Bootstrap Icons not loading on deform forms

## Problem

After upgrading deform (Pylons/deform), the component moved from Bootstrap 3/4
glyphicons to **Bootstrap 5 + Bootstrap Icons**. The sequence widget action
buttons (add / remove / move item) render as `<i class="bi bi-...">` elements,
so without the icon font stylesheet they appeared as empty grey buttons in the
"Field assist" form.

## Diagnosis

- `src/static/deform/css/bootstrap-icons.min.css` and the font files
  (`src/static/deform/css/fonts/bootstrap-icons.woff{,2}`) were already copied
  from the deform project and the relative `url("fonts/...")` references inside
  the stylesheet resolve correctly.
- `src/templates/utils/field_assist.html` is the only template that includes
  deform's CSS. It linked `bootstrap.min.css` and `form.css` plus the
  per-widget resources returned by `form.get_widget_resources()`, but
  `bootstrap-icons.min.css` is **not** part of the widget resource registry, so
  it was never added to the page.

## Change

`src/templates/utils/field_assist.html`: added the missing stylesheet link
between `bootstrap.min.css` and `form.css`:

```html
<link rel="stylesheet" href="{% static 'deform/css/bootstrap-icons.min.css' %}" type="text/css"/>
```

## Follow-up: clipped `<select>` labels

The selected option label was rendered cut off vertically. Same class of
conflict: `base.html` loads the legacy **Bootstrap 2** stylesheet
(`static/bootstrap/css/bootstrap.min.css`), which contains

```css
select, input[type="file"] { height: 28px; *margin-top: 4px; line-height: 28px }
```

Bootstrap 5's `.form-select` (padding `.375rem .75rem` + `line-height: 1.5`)
needs roughly 38px, but it never declares a `height`, so the BS2 element-level
rule wins unopposed and clips the text. The template already had this exact
workaround for `input[type="text"]`; it was extended to `select` (keeping
`height: auto` for multi-selects, which BS2 also special-cased).

## Follow-up: standalone base template for the popup

Rather than keep patching individual controls, the field assist popup no longer
extends `base.html` at all.

New file `src/templates/utils/field_assist_base.html`: a minimal standalone
skeleton that loads **only** the Bootstrap 5 shipped with deform
(`bootstrap.min.css`, `bootstrap-icons.min.css`, `form.css`), the per-widget
resources from `form.get_widget_resources()`, and deform's jQuery. It drops
everything the popup never used anyway: Bootstrap 2 + `bootstrap-responsive`,
`font-awesome`, `screen.css`, the menu / breadcrumb / footer, the loading mask,
`lang.html` and `alert.html` (the view passes no `alert`, and the language
switcher UI lives in the menu, which the popup hides).

`src/templates/utils/field_assist.html` now extends it and only carries the
form-specific CSS. Consequences:

- The `input[type="text"] / select { height: initial }` hacks were **removed** —
  they only existed to undo Bootstrap 2, which is no longer loaded.
- The `.panel`, `.panel-heading` and `.panel-footer` rules were **dead**: those
  are Bootstrap 3 names, and deform 3.0.1 renders `.card`, `.card-header` and
  `.card-footer`. They were ported to the Bootstrap 5 names, which restores the
  pre-upgrade look (hidden item header, borderless card).
- `ul { padding-left: 0 }` was added: Bootstrap 2 zeroed the list padding, but
  Bootstrap 5 sets `padding-left: 2rem`, which would indent the fields rendered
  by the custom `templates/deform/mapping_item.pt`.

## Verification

- `make dev_check` (new Makefile target, `manage.py check`) — no issues.
- `POST /utils/field_assist/author_keyword/` returns 200 and the rendered page
  links only the deform Bootstrap 5 assets (no `bootstrap/css/bootstrap.min.css`,
  no `screen.css`, no font-awesome).
- All four deform CSS assets and `fonts/bootstrap-icons.woff2` return 200.
- The rendered markup confirms `card` / `card-header` / `card-footer`,
  `form-select` and `bi bi-*` classes, matching the CSS above.
- No visual/screenshot check was performed (headless Chrome would not run in
  this environment), so the popup layout still needs a look in the browser.

## Follow-up: reorder button did nothing

`deform/templates/sequence_item.pt` (deform 3.0.1) renders both sequence
buttons with no `type` attribute:

```html
<button class="deform-order-button btn bi bi-arrows-vertical" ...></button>
<button class="deform-close-button btn bi bi-x" ... onclick="javascript:deform.removeSequenceItem(this);"></button>
```

Inside `<form id="deform">` a `<button>` without `type` defaults to
`type="submit"`. `jquery-sortable` binds the drag to `mousedown` and its default
`onMousedown` only calls `preventDefault()`, which does not suppress the
subsequent `click` — so releasing the mouse at the end of a drag (or a plain
click on the handle) submitted the form and reloaded the popup, discarding the
new order.

The same bug affected the remove button: its inline `onclick` calls
`deform.removeSequenceItem(this)` but never returns `false`, so the item was
removed and the form submitted anyway.

Fix: new override `src/templates/deform/sequence_item.pt` — a copy of the
upstream template with `type="button"` added to both buttons and nothing else
changed. The view already registers `src/templates/deform` ahead of the deform
package in the ZPT search path (`utils/views.py:136-140`), the same mechanism
already used for `mapping_item.pt`.

Overriding the template rather than patching in JavaScript matters here: deform
serialises this template into the `prototype` attribute that `deform.js` uses to
build items added at runtime, so the fix covers dynamically added rows for free.

Note the sortable handle is `".deform-order-button, .card-header"`; since
`.card-header` is hidden (see above), dragging works from the reorder icon only.

## Verification of the reorder fix

- The rendered page and the decoded `prototype` attribute both show
  `<button type="button" class="deform-order-button ...">` and
  `deform-close-button`.
- The explanatory header uses the Chameleon non-rendering comment form
  (`<!--! ... -->`), confirmed absent from both the page and the prototype.
- `make dev_check` and `make dev_test_app app=utils` (13 tests) pass.
- Drag and drop itself was not exercised in a browser here; please confirm the
  reorder interaction in the popup.

## Follow-up: hide reorder, style Add/Remove as secondary buttons

Drag and drop reordering was judged unintuitive, so the handle is hidden and the
two remaining actions were given a real button look.

- `src/templates/utils/field_assist.html`: added

  ```css
  .deform-order-button { display: none !important; }
  ```

  `!important` is required — `deform.js` `processSequenceButtons()` toggles this
  button with jQuery `.toggle()`, which writes an inline `display` style that
  would otherwise win.

- `src/templates/deform/sequence_item.pt`: the remove button now carries
  `btn btn-secondary bi bi-x`.

- New override `src/templates/deform/sequence.pt`: a copy of the upstream
  template whose only change is `class="btn btn-secondary deform-seq-add"` on
  the "Add ..." link. Forking the template (rather than adding the class from
  JavaScript) keeps nested sequences correct, since deform serialises these
  templates into the `prototype` used for rows created at runtime.

Both overrides start with a Chameleon non-rendering comment (`<!--! ... -->`)
recording what was changed against upstream, so a future deform upgrade can be
reconciled. That is the trade-off accepted here: two forked templates to
maintain.

Reordering is now unreachable in the UI (`.card-header`, the other sortable
handle, is hidden too) while the sortable JavaScript still initialises. If the
intent is to drop reordering for good, the cleaner change is
`deform.widget.SequenceWidget(..., orderable=False)` at `utils/views.py:171`,
which stops emitting the button and the sortable setup altogether.

Verified on the rendered page and inside the decoded `prototype` attribute:
`btn btn-secondary deform-seq-add`, `deform-close-button btn btn-secondary
bi bi-x`, the hide rule present, and no override comment leaking into the
output. `make dev_check` and `make dev_test_app app=utils` (13 tests) pass.

## Deploy note

In production the new CSS/font files need to be published:

```
make prod_exec_collectstatic
```
