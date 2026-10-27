# Admin-template-style text inputs

Matched FI-ADMIN's form fields to the admin template's `.form-control`. The values were read from the live page's computed styles.

## Admin template reference
13px text, 19.5px line-height, 8px × 14.4px padding, 37.5px tall, 1px `#ced4da` border, 4px radius, white fill, `#212529` text. On focus only the border changes, to `#b3b9d0`; the admin template's focus box-shadow (`0 0 1 .25rem`) is invalid CSS and never renders. Placeholder `#878a99`.

## Changes (`src/static/css/screen.css`)
- Text-like inputs, textareas and `.uneditable-input`: 8px × 14px padding, 19.5px line-height, 37.5px tall, 4px radius, `#ced4da` border, no inset shadow, 0.15s border/shadow transition.
- They stay `content-box` (Bootstrap 2's model), so `input-mini`…`input-xxlarge` and fixed px widths keep their typing room. Each field is 20px wider overall than before.
- Single selects use the same content-box metrics, so an input and a select of the same width end at the same edge. Multi-selects keep their own height.
- Input-append/prepend add-ons and their corners match. The multiple-select plugin trigger (`.ms-choice`) is 37.5px with matching padding and colors.
- `--focus-border` is now `#b3b9d0` (admin template). The 3px indigo focus ring is kept, because a border change alone is not a visible focus indicator.
- The default `.btn` gets the same 37.5px height (8px × 14px padding), so search and Apply buttons sit level with the fields. `.btn-large`, `.btn-small` and `.btn-mini` are restated at their Bootstrap 2 sizes.
- The placeholder stays `--muted` (`#686d80`, 5.2:1); the admin template's `#878a99` is only 3.4:1.

## Docs
`DESIGN.md`: input and button tokens and the Inputs / Fields section updated.

## Verification
Headless Chromium on the dev app at 1440px: events filter row (input, selects and button all 37.5px, same top), new event form (status select and title input both end at x=881), indexing tab, bibliographic advanced filters, dashboard.

## Known
- In the bibliographic filter tray, "Networks" wraps to a second line, mainly because the Collection plugin is about 530px wide.
- The "Add descriptor/keyword" buttons and "delete" links in formsets render in a serif font. This was already the case and was not changed.
