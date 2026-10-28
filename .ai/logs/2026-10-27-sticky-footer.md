# Sticky footer fix

The footer left an empty band of page background below it on short pages.

## Cause
`.wrap` used `min-height: 84%` of the viewport to push the footer down. On short pages the footer ended at 84% + its own height, leaving the rest of the viewport empty below it.

## Fix (`src/static/css/screen.css`)
- `html` keeps `height: 100%`. `body` becomes a flex column with `min-height: 100%` instead of a fixed `height: 100%`.
- `.wrap` drops `min-height: 84%` and gets `flex: 1 0 auto`, so it fills the space above the footer.
- `#footer` gets `flex: none`.
- `DESIGN.md` layout section notes the sticky footer.

## Verification
Headless Chromium on the dev app: the footer's bottom edge equals the viewport height on events (1909×971), login (1909×971) and mobile (390×800). On the long new-event form it sits right after the content at the end of the document.
