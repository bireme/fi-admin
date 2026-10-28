# Mobile list header and search form

On phones, the "New …" button on list pages covered the page title (H2), and the search form fell into a staggered layout.

## Cause
- `.header .pull-right { margin-top: -35px }` pulled the actions up onto the title line at every width. Once the title and button no longer fit side by side, the button landed on top of the title.
- Search forms put fixed-width fields and bare-text labels inline inside `.input-append`. Bootstrap's input-append adds a `-5px !important` side margin to the input and a joined border to the button, which pushed both past the panel edge.

## Fix (`src/static/css/screen.css`)
- `.header:has(> .pull-right)` is now a wrapping flex row: title on the left, actions on the right, centered vertically. A title that doesn't fit pushes the actions onto their own row instead of overlapping them. This applies at all widths, so long PT/ES titles on narrow desktop windows are covered too. The old negative margin is still there as a fallback for browsers without `:has()`.
- Below 768px:
  - the list H2 is 20px/26px and the actions wrap left-aligned under it;
  - `form[name="search"]` becomes a wrapping flex row. The text field, selects and advanced-filter selects are full width at 37.5px tall, so each inline label sits on its own line above its field. The text field keeps the search button beside it only when the button follows it directly (simple input + button forms);
  - the input-append side margins and joined corners are reset, and the buttons get their own 4px corners.

## Verification
Rendered the bibliographic records list (EN and PT-BR, advanced filters open) and the events list as an existing user, then took screenshots with headless Chromium at 360, 390, 430, 800, 1024 and 1440px. There's no horizontal overflow, the title and button never overlap, and desktop layout is unchanged apart from the button now being vertically centered on the title. Note that `chromium --headless=new` has a minimum window width of about 500px, so narrower screenshots need the Playwright `chrome-headless-shell`.

## Not addressed
- Wide list tables (for example events: dates plus status plus actions) still overflow the panel on phones.
- A leading `&nbsp;` in the templates indents the first inline label (for example "Record type:") by a few pixels on mobile.
