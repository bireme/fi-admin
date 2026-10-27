# JSON field display styled as an input

`.jsonfield_display` is the read-only box for JSONField values on bibliographic, title, institution, multimedia, legislation and OER forms. It is a `<ul>` inside a link that opens the field assistant. It now matches the Velzon-style text inputs.

## Changes (`src/static/css/screen.css`)
- White fill (was the gray Tray), `#ced4da` border, 4px corners, 8px × 14px padding, 13px text on 19.5px lines. Its 560px content width now ends at the same edge as the 560px inputs and textareas (590px outer). The 30px left offset is kept because it compensates for the `.row` wrapper.
- Text is Ink instead of inheriting the indigo link color; keys (`<strong>`) are Heading. List bullets removed; items are 4px apart.
- The wrapping link is `inline-block` and not underlined. Hover moves the border to Focus Border. Keyboard focus shows the indigo focus ring on the box instead of the browser outline on the link.
- Cursor is `pointer` (was `context-menu`), because a click opens the assistant.
- `DESIGN.md` Inputs / Fields entry updated.

## Verification
Headless Chromium on `/bibliographic/new-source?document_type=S`, call number field: left/right edges 266/856px, the same as the textarea below. Checked filled with two sample items, empty, and keyboard-focused.
