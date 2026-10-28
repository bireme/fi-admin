---
name: FI-ADMIN
description: Back-office cataloging workspace for the BIREME/PAHO/WHO Virtual Health Library network.
colors:
  indigo: "#405189"
  indigo-deep: "#364574"
  indigo-soft: "rgba(64, 81, 137, 0.1)"
  sidebar-text: "#c3cdf0"
  focus-border: "#b3b9d0"
  ground: "#f3f3f9"
  panel-white: "#ffffff"
  tray: "#f3f6f9"
  ink: "#212529"
  heading: "#495057"
  muted: "#686d80"
  border: "#e9ebec"
  border-faint: "#f1f2f5"
  input-border: "#ced4da"
  footer-indigo: "#2a3352"
  success: "#0ab39c"
  success-deep: "#08776a"
  success-fill: "#08806f"
  danger: "#f06548"
  danger-deep: "#a83822"
  danger-fill: "#c94a33"
  warning: "#f7b84b"
  warning-deep: "#875c0e"
  info: "#299cdb"
  info-deep: "#1a6fa0"
  info-fill: "#1b78ae"
  pending: "#b8520b"
typography:
  display:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: "36px"
  headline:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: "36px"
  title:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: "27px"
  subtitle:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: "18px"
  body:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: "18px"
  label:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: "14px"
  wordmark:
    fontFamily: "\"Helvetica Neue\", Helvetica, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 200
    lineHeight: 1
rounded:
  sm: "3px"
  md: "4px"
  lg: "5px"
  modal: "6px"
  pill: "9px"
spacing:
  xs: "4px"
  sm: "10px"
  md: "20px"
  lg: "30px"
  xl: "40px"
components:
  button-default:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
  button-primary:
    backgroundColor: "{colors.indigo}"
    textColor: "{colors.panel-white}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
  button-primary-hover:
    backgroundColor: "{colors.indigo-deep}"
    textColor: "{colors.panel-white}"
  button-large:
    rounded: "{rounded.lg}"
    padding: "9px 14px"
  button-danger:
    backgroundColor: "{colors.danger-fill}"
    textColor: "{colors.panel-white}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
  input:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
    height: "37.5px"
  sidebar:
    backgroundColor: "{colors.indigo}"
    textColor: "{colors.panel-white}"
    width: "224px"
  sidebar-collapsed:
    backgroundColor: "{colors.indigo}"
    width: "56px"
  sidebar-link:
    textColor: "{colors.sidebar-text}"
    rounded: "{rounded.md}"
    padding: "0 10px"
    height: "36px"
  sidebar-link-active:
    backgroundColor: "rgba(255, 255, 255, 0.14)"
    textColor: "{colors.panel-white}"
  content-panel:
    backgroundColor: "{colors.panel-white}"
    rounded: "{rounded.lg}"
  footer:
    backgroundColor: "{colors.footer-indigo}"
    textColor: "{colors.panel-white}"
    height: "90px"
  status-label:
    textColor: "{colors.success-deep}"
    backgroundColor: "rgba(10, 179, 156, 0.12)"
    rounded: "{rounded.sm}"
    padding: "1px 4px 2px"
---

# Design System: FI-ADMIN

## Overview

**Creative North Star: "The Cataloguer's Desk"**

FI-ADMIN is a dependable desk for long sessions of record entry. There is a cool, pale lavender-gray ground. Each task gets one white panel with a faint border and a whisper of shadow. A soft indigo sidebar runs down the left edge, and a deep indigo band at the foot carries BIREME's mark. The palette follows the admin template: low-contrast chrome, tinted rather than saturated status fills. The design never competes with the record. Documentalists and editors spend hours on dense, tabbed, methodology-bound forms in three languages, so the system favors legibility, predictability, and familiar controls over expression.

The system is Bootstrap 2.0.4 with a thin house layer (`src/static/css/screen.css`). The house layer is where identity lives: the indigo sidebar, the cool ground, the panel-with-breadcrumb-cap layout, and the status colors that mark a record's lifecycle. Everything else is Bootstrap 2 idiom. Center staff across the network already know these controls, and that familiarity is a feature.

The direction from here is **flatten gradually**. Keep every structure users rely on: tabs, modals, striped tables, the panel layout, the button hierarchy. Treat Bootstrap 2's gradients, inset highlights, and text-shadows as dated surface finish. New and reworked pieces render flat, using the same colors, radii, and spacing.

**Key Characteristics:**
- Cool #f3f3f9 ground with white working panels; one panel per page.
- One indigo carries both the sidebar and the primary action, as in the admin template. Everything else is neutral or tinted.
- Bootstrap 2's gradients are replaced by a flat skin in `screen.css`: solid buttons, soft tinted labels and alerts, quiet focus rings.
- 13px/18px Helvetica Neue body at high density, built for field-heavy forms.
- Gentle 3–5px corners throughout, with no sharp edges and no pills except badges.
- Depth comes from one structural shadow under the content panel, not from layered cards.
- Status is carried by color words (published, pending, deleted, draft), so they must stay consistent.

## Colors

A soft indigo palette after the admin template: cool neutral surfaces, one indigo for identity and action, and desaturated status colors shown mostly as tints. All tokens live as CSS custom properties on `:root` in `src/static/css/screen.css`; new rules use the variables, never literals.

### Primary
- **Indigo** (`--primary`, `--sidebar-bg`): The sidebar and mobile bar fill, links, primary buttons, active tabs, pagination and checkbox accent. White on it reaches 7.6:1.
- **Indigo Deep** (`--primary-deep`): Hover and pressed state of primary buttons and links.
- **Indigo Soft** (`--primary-soft`): Tinted backgrounds for selected states. The focus ring is a 3px 15% indigo halo with the border shifted to **Focus Border** (`--focus-border`).
- **Sidebar Text** (`--sidebar-text`): Resting text and icons on the indigo (items, section labels, user line), at 4.8:1. Hover and the current page turn white; the current page also gets a 14% white wash and bold weight.

### Semantic status
Each status has a base hue (for tints and borders), a **deep** text shade that passes 4.5:1 on white and on its own tint, and where needed a **fill** shade dark enough for white button text.
- **Success** (`--success` #0ab39c, `--success-deep`, `--success-fill`): Published records, success labels and alerts.
- **Danger** (`--danger` #f06548, `--danger-deep`, `--danger-fill`): Errors, required asterisks, destructive buttons, deleted records.
- **Warning** (`--warning` #f7b84b, `--warning-deep`): Warning labels and the default Bootstrap alert. Warning buttons use the base fill with Ink text.
- **Info** (`--info` #299cdb, `--info-deep`, `--info-fill`): Info labels, count badges, info alerts.
- **Pending** (`--pending`): Records awaiting review (`.status-pending`).
- Labels and badges are soft: a 10–20% tint of the hue with deep text, no text-shadow. Alerts follow the same pattern with a slightly stronger tinted border. `label-salmon` and `label-lilac` are soft too.

### Neutral
- **Ground** (`--ground`): The page background behind every panel.
- **Panel White** (`--surface`): Content panels, inputs, modals, dropdowns, breadcrumb.
- **Tray** (`--tray`): Hover rows, wells, the advanced-filters tray, input add-ons, read-only JSON boxes, tab hover.
- **Ink** (`--ink`): Body text and labels. **Heading** (`--heading`) is a lighter slate for h1–h6 and page titles.
- **Muted** (`--muted`): Help text (`.muted`), placeholders, metadata, timestamps, breadcrumb trail, inactive tabs. 5.2:1 on white, 4.6:1 on the ground.
- **Border** (`--border`): Panel and breadcrumb borders, table rules, header and form-submit rules, tabs. **Border Faint** separates dashboard list rows. **Input Border** (`--input-border`) outlines form controls and default buttons.
- **Footer Indigo** (`--footer-bg`): The footer band. It stays dark because the BIREME/PAHO/WHO logos are white artwork.

### Named Rules
**The One Indigo Rule.** Indigo is the only chromatic accent in chrome and interaction. Do not introduce a second brand or action color; reach for a tint of indigo or a neutral first.

**The Status Vocabulary Rule.** Status colors mean record states, not decoration. Use Danger, Pending, Success, Warning or Info only where they report state, alert, or destroy. Text in a status color always uses the `-deep` shade.

## Typography

**Body Font:** Helvetica Neue (with Helvetica, Arial, sans-serif)

**Character:** A single neutral grotesque throughout. Hierarchy comes from size and weight, not from font pairing. The only expressive moment is the ultra-light 20px "FI-ADMIN" wordmark at the head of the sidebar.

### Hierarchy
- **Display** (700, 30px, 36px): Rare. Used for standalone pages such as errors and sign-in.
- **Headline** (700, 24px, 36px): Section titles on dashboards and reports.
- **Title** (400, 18px, 27px): The page header on list and edit pages (`.header h3`). It is deliberately set at normal weight, with an icon to its left and actions floated right.
- **Subtitle** (700, 14px, 18px): Group headings inside forms and record previews.
- **Body** (400, 13px, 18px): Everything else: form labels, inputs, table cells, help text. Help asides step up to 14pt with 140% leading for reading.
- **Label** (700, 11px, 14px): Status labels and badges, the version string, and small uppercase eyebrows such as the help heading.

### Named Rules
**The Three Languages Rule.** Every text container must fit Portuguese and Spanish strings, which are often 20–30% longer than English. Never fix a width around an English label.

## Layout

The page has two columns. A fixed sidebar on the left is 224px wide expanded and 56px collapsed, and the collapsed choice is remembered per browser. Everything else (the `.wrap` content and the footer) shifts right by the sidebar width. In that column, a breadcrumb strip is fused to the top of a single white content panel (20px margins). A deep indigo footer (at least 80px tall) sits at the bottom: the body is a flex column and `.wrap` grows to fill the space, so on short pages the footer meets the bottom edge of the viewport with no gap. Below 768px, the sidebar becomes an off-canvas drawer behind a 48px deep-green mobile bar. The breadcrumb and panel read as one object: the breadcrumb drops its bottom radius and the panel drops its top border.

Inside the panel, Bootstrap 2's fluid 12-column grid (`container-fluid`, `row-fluid`, `spanN`) is the layout tool. Pages follow one of three shapes:

- **List pages:** a header row (title left, actions right, rule beneath), an optional advanced-filter tray, a striped or condensed table, and centered pagination 40px below.
- **Edit pages:** a header, horizontal tabs (`nav-tabs`) splitting long methodology forms into groups, fieldsets with formset rows and add/remove icons, and a form-submit bar with a top rule and 40px separation.
- **Preview pages:** the same tabs with inputs hidden and labels bold inline. A record reads as a definition list.

Spacing runs on a loose 10/20/30/40px rhythm. Field rows sit 4px apart, which is dense on purpose. Form controls in the legacy forms often have fixed pixel widths (for example 540–560px metadata fields). Responsive behavior relies on `bootstrap-responsive` and is secondary: this is a desktop work tool.

### Named Rules
**The One Desk Rule.** Each page has exactly one white content panel on the ground. Group content with tabs, fieldsets, wells, and rules inside it, never with a second floating card.

## Elevation & Depth

The system is mostly flat, with one structural lift. The content panel sits above the ground on a whisper-soft shadow, and that is the main depth cue in the product. Modals and dropdowns use Bootstrap 2's own overlay shadows. The sign-in form uses a barely-there lift. Everything inside the panel is flat: tables, tabs, fieldsets, and wells are separated by hairlines and tonal fills.

### Shadow Vocabulary
- **Panel lift** (`--shadow-card`: `0 1px 2px rgba(56, 65, 74, 0.15)`): The main content panel and the sign-in form.
- **Overlay** (`--shadow-overlay`: `0 5px 10px rgba(30, 32, 37, 0.12)`): Dropdowns and the sidebar tooltip; modals use a deeper `0 8px 30px` version.
- **Focus ring** (`--focus-ring`: `0 0 0 3px rgba(64, 81, 137, 0.15)`): Focused inputs and keyboard-focused buttons, with the input border shifting to Focus Border. Invalid required fields use the same ring in danger.

### Named Rules
**The Single Lift Rule.** Only the content panel and true overlays (modal, dropdown, toast alerts) cast shadows. Nothing inside the panel is elevated.

## Shapes

Corners are gently softened everywhere and never sharp or fully round: 3px on inputs and status labels, 4px on buttons and alerts, 5px on the content panel and large buttons, 6px on modals, and 9px pills only for numeric badges. Borders are 1px hairlines. The breadcrumb and panel share one rounded silhouette, with the inner corners squared where they meet. Icons come from Font Awesome 3 (`icon-*` classes) at text size, with 24px for emphasis (`.icon-m`).

## Components

### Buttons
Familiar Bootstrap 2 buttons, moving toward flat.
- **Shape:** gently rounded (4px; 5px for large).
- **Default:** flat white with Ink text and an Input Border outline; hover fills with Tray. Same 37.5px height as inputs (8px × 14px padding), so buttons sit level with the fields beside them. Small and mini keep the Bootstrap 2 sizes; large stays 9px × 14px at 15px.
- **Primary:** Indigo, white text, Indigo Deep on hover. It marks the single main action of a form or header (Save, New record).
- **Danger:** Danger Red, used for delete and confirm-delete only.
- **Large:** the standard size for form-submit bars and header actions (it appears 127 times in the templates).
- **Hover / Focus:** every variant is flat and shifts to a deeper shade on hover; keyboard focus shows the indigo focus ring.
- **Legacy one-off:** `.btn-decs`, a gray gradient with right-only rounding attached to the DeCS lookup field. Don't replicate it. New lookup affordances use a default button attached with an input-append.

### Status Labels & Badges
- **Style:** small bold white text on a semantic fill, 3px corners. Badges are 9px pills for counts.
- **House variants:** `label-salmon` (`#fa8072`) and `label-lilac` (`#c8a2c8`) extend the status set for record types. Keep them to existing meanings.

### Content Panel
- **Corner Style:** 5px, squared at the top where it meets the breadcrumb.
- **Background:** Panel White on Ground.
- **Shadow Strategy:** Panel lift (see Elevation & Depth).
- **Border:** 1px Border.
- **Internal Padding:** 10px top, 30px bottom, with grid gutters at the sides.

### Inputs / Fields
- **Style:** Admin template `.form-control` metrics: white field, 1px Input Border, 4px corners, 13px text on a 19.5px line, 8px × 14px padding, 37.5px tall. Text inputs and single selects stay `content-box`, so the `input-mini`…`input-xxlarge` classes and fixed px widths keep their typing room, and an input and a select of the same width end at the same edge. Multi-selects keep their own height. The multiple-select plugin trigger (`.ms-choice`) is sized to match.
- **Focus:** the border turns Focus Border (`#b3b9d0`, the admin template's soft primary) and the 3px indigo focus ring appears. The admin template's own ring is invalid CSS and never renders; the ring is kept because a border change alone is not a visible focus indicator.
- **Error:** Django errorlists are converted to `alert alert-error` blocks (red text on a pale red fill) above the field.
- **Required:** a red asterisk (`span.mark`, `#e32`) and a bold black label.
- **Help:** labels with help use a dotted underline and a help cursor (`.field_with_help`) and open a help modal.
- **Read-only JSON display:** `.jsonfield_display` (a `<ul>` inside a link that opens the field assistant) is styled as a text input: white, Input Border, 4px corners, 8px × 14px padding, 19.5px lines, 560px content width so it ends with the 560px inputs and textareas. Each JSON item is one line, with keys in bold Heading. Hover shifts the border to Focus Border, and keyboard focus on the link shows the focus ring. Empty, it reads as a blank field.

### Navigation
- **Sidebar:** fixed on the left, Indigo, 224px expanded and 56px collapsed (icons only). From top to bottom:
  - The "FI-ADMIN" wordmark (20px, weight 200; "FI" when collapsed), linking to the dashboard.
  - A Dashboard link.
  - The "Information Source" section, which lists the source types.
  - A divided group with Suggestions, Error reports and Reports.
  - For superusers, the expandable "Controlled lists" group and Admin.
  - A pinned footer with the EN/PT/ES switch, the user name and center code, Logout, and the collapse toggle.
  - Items appear only for the user's service roles.
- **Sidebar items:** 36px rows with 4px corners. Each has a 20px Font Awesome icon and a label, and every item has its own icon so the collapsed rail stays readable. Items rest in Sidebar Text; hover adds a 7% white wash and white text. The current page gets a 14% white wash with white bold text (`aria-current="page"`). While collapsed, labels stay in the accessibility tree and appear as an Ink tooltip on hover or focus. Opening "Controlled lists" while collapsed expands the sidebar first.
- **Mobile bar:** below 768px, a fixed 48px indigo bar with a menu button and the wordmark. It opens the sidebar as a 264px drawer over a 40% black scrim. Escape or a click on the scrim closes it.
- **Dropdowns:** white menus with an overlay shadow; the hovered item gets a Tray fill, the active one indigo text.
- **Breadcrumb:** a flat white strip capping the content panel, 11pt, Muted trail and Ink current item.
- **Tabs:** Bootstrap `nav-tabs` split long record forms into methodology groups. The active tab joins the panel surface.
- **Language switch:** EN / PT / ES as a segmented row in the sidebar footer (stacked when collapsed). All three are always visible, and the current one is filled white with Indigo text.

### Dashboard Widgets
- **Style:** flat sections inside the content panel, separated by Border top rules, not wells or cards. Each head has a 14px bold title and, for on-demand lists, a small default "Check" button on the right.
- **Lists:** rows with a muted 14px icon, a title that wraps, and a right-aligned tabular timestamp in Muted Text, separated by faint rules.
- **States:** a spinner while loading (`aria-busy`), a "No records found" empty line, and a red "Could not load this list. Try again." error line. Results are announced politely.

### Tables
- **Style:** row rules only (1px `#ddd` bottom border, no top border), with 11px vertical cell padding on list tables. `table-striped` and `table-condensed` are the common variants.

### Modals & Alerts
- **Modals:** Bootstrap 2 modals, used heavily (help, dedup, change log, confirmations). The help modal is widened to 750px.
- **Alerts:** inline `alert-error` and `alert-info` are the common variants. Floating toast alerts stack bottom-right at 500px wide.
- **Loading mask:** a full-screen 70% white veil with a centered spinner GIF during form submissions.

### Footer
A 90px Footer Indigo band. The language-specific BIREME/PAHO/WHO logo sits on the left. Terms and Privacy links in light gray and the app version in Muted sit on the right. The logo and links are mandatory on every authenticated and public page.

## Do's and Don'ts

### Do:
- **Do** keep exactly one white content panel per page on the Ground, capped by the breadcrumb.
- **Do** use the CSS variables on `:root` for every color; never add hex literals to new rules.
- **Do** give every sidebar entry its own distinct icon. The collapsed rail is icons only.
- **Do** build new pieces flat: solid fills, the existing colors and 3–5px radii, with no gradients, inset highlights, or text-shadows.
- **Do** keep Bootstrap 2 structures (nav-tabs, modals, striped tables, wells, input-append) so center staff never relearn the interface.
- **Do** size text containers for PT-BR and ES strings, and pass all copy through `{% trans %}`.
- **Do** report record state with the status colors consistently: published, pending, deleted, draft.

### Don't:
- **Don't** put status hues at full strength behind text; use the soft tint with the `-deep` text shade.
- **Don't** put small white text on the base status hues (success, danger, info, warning). Use the `-fill` shades.
- **Don't** reintroduce a top navigation bar. Navigation lives in the left sidebar.
- **Don't** add shadows inside the content panel or nest floating cards in it.
- **Don't** introduce new fonts. Helvetica Neue / Arial is the only family.
- **Don't** add new gradient or bevel finishes such as `.btn-decs`. They are legacy to retire, not patterns to extend.
- **Don't** remove or restyle away the footer's BIREME/PAHO/WHO logo and policy links.
- **Don't** use semantic status colors decoratively.
