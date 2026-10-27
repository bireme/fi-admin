# Soft indigo palette (Velzon reference)

Softened the application colors using the Velzon admin theme (themesbrand.com/velzon) as reference. The user chose to adopt Velzon's indigo for the sidebar and primary color in place of BIREME green.

## `src/static/css/screen.css`
- New color tokens as CSS custom properties on `:root` (indigo #405189, ground #f3f3f9, borders #e9ebec, muted #686d80, soft status hues with `-deep` text and `-fill` button shades). House rules now use the variables instead of hex literals.
- Sidebar and mobile bar: indigo fill, #c3cdf0 resting text, white hover/current text; the current item is a 14% white wash instead of a white pill.
- Page: cool ground, white panel with #e9ebec border and a whisper shadow, flat white breadcrumb, deep indigo footer (logos are white artwork).
- New "Bootstrap 2 soft skin" section: flat buttons in every variant (no gradients, text-shadows or inset highlights), indigo links/tabs/pagination, soft tinted labels, badges and alerts, quieter input focus ring, Tray-colored wells/add-ons/table hover, softer dropdowns and modals, `.muted` and `.text-*` contrast fixes, accent/caret/selection colors.
- `.btn-decs` flattened; `.wrap` border made transparent.

## Contrast
All text colors were checked to reach 4.5:1 on their backgrounds (sidebar text 4.8:1 on indigo, muted 5.2:1 on white; status text uses the `-deep` shades; white button text uses the `-fill` shades).

## Docs
- `DESIGN.md` colors, components, elevation and do/don't rules rewritten for the indigo palette. `.impeccable/design.json` sidecar was not regenerated.

## Verification
Logged into the dev app (`make dev_up`) and screenshotted dashboard, events list, new event form (including focus and invalid states), titles, bibliographic list, thesaurus and login at 1440px in headless Chromium.
