---
name: FI-ADMIN
description: Back-office cataloging workspace for the BIREME/PAHO/WHO Virtual Health Library network.
colors:
  bireme-green: "#00ba8b"
  bireme-green-deep: "#00704f"
  bireme-green-ink: "#00563a"
  sidebar-mint: "#c8f5e6"
  action-blue: "#0088cc"
  action-blue-deep: "#0055cc"
  paper: "#f9f6f1"
  panel-white: "#ffffff"
  ink: "#333333"
  charcoal: "#414141"
  hairline: "#d6d6d6"
  rule-soft: "#eeeeee"
  filter-tray: "#f5f5f5"
  muted: "#999999"
  muted-text: "#767676"
  danger-red: "#b94a48"
  success-green: "#468847"
  warning-amber: "#f89406"
  info-steel: "#3a87ad"
  pending-orange: "#e66f00"
  notice-mint: "#b2eadc"
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
    padding: "4px 10px"
  button-primary:
    backgroundColor: "{colors.action-blue}"
    textColor: "{colors.panel-white}"
    rounded: "{rounded.md}"
    padding: "4px 10px"
  button-primary-hover:
    backgroundColor: "{colors.action-blue-deep}"
    textColor: "{colors.panel-white}"
  button-large:
    rounded: "{rounded.lg}"
    padding: "9px 14px"
  button-danger:
    backgroundColor: "{colors.danger-red}"
    textColor: "{colors.panel-white}"
    rounded: "{rounded.md}"
    padding: "4px 10px"
  input:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "4px"
    height: "18px"
  sidebar:
    backgroundColor: "{colors.bireme-green-deep}"
    textColor: "{colors.panel-white}"
    width: "224px"
  sidebar-collapsed:
    backgroundColor: "{colors.bireme-green-deep}"
    width: "56px"
  sidebar-link:
    textColor: "{colors.panel-white}"
    rounded: "{rounded.md}"
    padding: "0 10px"
    height: "36px"
  sidebar-link-active:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.bireme-green-ink}"
  content-panel:
    backgroundColor: "{colors.panel-white}"
    rounded: "{rounded.lg}"
  footer:
    backgroundColor: "{colors.charcoal}"
    textColor: "{colors.panel-white}"
    height: "90px"
  status-label:
    textColor: "{colors.panel-white}"
    rounded: "{rounded.sm}"
    padding: "1px 4px 2px"
---

# Design System: FI-ADMIN

## Overview

**Creative North Star: "The Cataloguer's Desk"**

FI-ADMIN is a dependable desk for long sessions of record entry. There is a warm paper ground. Each task gets one white panel with a hairline border and a soft lift. A deep-green institutional sidebar runs down the left edge, and a charcoal band at the foot carries BIREME's mark. The design never competes with the record. Documentalists and editors spend hours on dense, tabbed, methodology-bound forms in three languages, so the system favors legibility, predictability, and familiar controls over expression.

The system is Bootstrap 2.0.4 with a thin house layer (`src/static/css/screen.css`). The house layer is where identity lives: the BIREME green sidebar, the paper background, the panel-with-breadcrumb-cap layout, and the status colors that mark a record's lifecycle. Everything else is Bootstrap 2 idiom. Center staff across the network already know these controls, and that familiarity is a feature.

The direction from here is **flatten gradually**. Keep every structure users rely on: tabs, modals, striped tables, the panel layout, the button hierarchy. Treat Bootstrap 2's gradients, inset highlights, and text-shadows as dated surface finish. New and reworked pieces render flat, using the same colors, radii, and spacing.

**Key Characteristics:**
- Warm paper ground with white working panels; one panel per page.
- Green marks identity (the left sidebar) and blue marks action. The two never swap roles.
- 13px/18px Helvetica Neue body at high density, built for field-heavy forms.
- Gentle 3–5px corners throughout, with no sharp edges and no pills except badges.
- Depth comes from one structural shadow under the content panel, not from layered cards.
- Status is carried by color words (published, pending, deleted, draft), so they must stay consistent.

## Colors

A muted institutional palette: warm neutral surfaces, one brand green for identity, Bootstrap blue for interaction, and a small semantic set for record status.

### Primary
- **BIREME Green** (`bireme-green`): The identity color in its brightest form. Its pale tint, **Notice Mint** (`notice-mint`), backs the system-wide maintenance notice band. White text on it only reaches 2.5:1, so it never carries small text.
- **BIREME Green Deep** (`bireme-green-deep`): The sidebar and mobile bar fill. It is the same hue, darkened so white 13px labels reach 6:1.
- **BIREME Green Ink** (`bireme-green-ink`): Text on the white active-item pill and on the selected language in the sidebar.
- **Sidebar Mint** (`sidebar-mint`): Secondary text on the deep green (section labels, user line, sub-items), at 5:1. It is a tint of the green, never a gray.

### Secondary
- **Action Blue** (`action-blue`): Links, primary buttons, active dropdown items, and informational icons (`.icon-blue`, status emphasis via `.color_status`). Every clickable affordance that isn't destructive is blue.
- **Action Blue Deep** (`action-blue-deep`): The pressed or hovered end of primary buttons.

### Tertiary (semantic status)
- **Danger Red** (`danger-red`): Error alerts, destructive buttons, and the remove-row icon in formsets.
- **Success Green** (`success-green`): Success labels and alerts. It is distinct from BIREME Green and never used for identity.
- **Warning Amber** (`warning-amber`): Warning labels and badges.
- **Info Steel** (`info-steel`): Info labels and alerts.
- **Pending Orange** (`pending-orange`): Records awaiting review (`.status-pending`).
- Published records use plain `green` (`.status-ok`), deleted ones use `#e32` (`.status-del`), and drafts use black (`.status-draft`). These literal values are legacy. New work should map them to Success Green, Danger Red, and Ink.

### Neutral
- **Paper** (`paper`): The page background behind every panel. It is slightly warm, never pure white.
- **Panel White** (`panel-white`): Content panels, inputs, modals, dropdowns.
- **Ink** (`ink`): All body text and labels.
- **Charcoal** (`charcoal`): The footer band and the sign-in heading.
- **Hairline** (`hairline`): Panel borders, breadcrumb borders, and table row rules (`#ddd` in tables).
- **Rule Soft** (`rule-soft`): Section dividers inside a panel: the page-header underline, the form-submit top rule, and the help aside's left bar.
- **Filter Tray** (`filter-tray`): The background of the advanced-filters tray on list pages.
- **Muted** (`muted`): Placeholders, footer secondary links, the version string (on dark or decorative contexts only).
- **Muted Text** (`muted-text`): Secondary text on white (metadata, timestamps, empty states). At 4.5:1 it replaces Muted for anything users need to read.

### Named Rules
**The Two Voices Rule.** Green says "this is BIREME", and blue says "you can act here". Inside the content panel, green never appears on a button or link, and blue never fills a bar or band. The sidebar is the one green band that holds links.

**The Status Vocabulary Rule.** Status colors mean record states, not decoration. Use Danger Red, Pending Orange, Success Green, or Info Steel only where they report state, alert, or destroy.

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

The page has two columns. A fixed sidebar on the left is 224px wide expanded and 56px collapsed, and the collapsed choice is remembered per browser. Everything else (the `.wrap` content and the footer) shifts right by the sidebar width. In that column, a breadcrumb strip is fused to the top of a single white content panel (20px margins). A charcoal footer (at least 80px tall) sits at the bottom. Below 768px, the sidebar becomes an off-canvas drawer behind a 48px deep-green mobile bar. The breadcrumb and panel read as one object: the breadcrumb drops its bottom radius and the panel drops its top border.

Inside the panel, Bootstrap 2's fluid 12-column grid (`container-fluid`, `row-fluid`, `spanN`) is the layout tool. Pages follow one of three shapes:

- **List pages:** a header row (title left, actions right, rule beneath), an optional advanced-filter tray, a striped or condensed table, and centered pagination 40px below.
- **Edit pages:** a header, horizontal tabs (`nav-tabs`) splitting long methodology forms into groups, fieldsets with formset rows and add/remove icons, and a form-submit bar with a top rule and 40px separation.
- **Preview pages:** the same tabs with inputs hidden and labels bold inline. A record reads as a definition list.

Spacing runs on a loose 10/20/30/40px rhythm. Field rows sit 4px apart, which is dense on purpose. Form controls in the legacy forms often have fixed pixel widths (for example 540–560px metadata fields). Responsive behavior relies on `bootstrap-responsive` and is secondary: this is a desktop work tool.

### Named Rules
**The One Desk Rule.** Each page has exactly one white content panel on the paper ground. Group content with tabs, fieldsets, wells, and rules inside it, never with a second floating card.

## Elevation & Depth

The system is mostly flat, with one structural lift. The content panel sits above the paper ground on a soft drop shadow, and that is the main depth cue in the product. Modals and dropdowns use Bootstrap 2's own overlay shadows. The sign-in form uses a barely-there lift. Everything inside the panel is flat: tables, tabs, fieldsets, and wells are separated by hairlines and tonal fills.

### Shadow Vocabulary
- **Panel lift** (`box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2)`): The main content panel only.
- **Whisper** (`box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05)`): The sign-in form.
- **Focus glow** (`box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(82,168,236,.6)`): Focused text inputs, together with the border shifting to `rgba(82,168,236,.8)`.

### Named Rules
**The Single Lift Rule.** Only the content panel and true overlays (modal, dropdown, toast alerts) cast shadows. Nothing inside the panel is elevated.

## Shapes

Corners are gently softened everywhere and never sharp or fully round: 3px on inputs and status labels, 4px on buttons and alerts, 5px on the content panel and large buttons, 6px on modals, and 9px pills only for numeric badges. Borders are 1px hairlines. The breadcrumb and panel share one rounded silhouette, with the inner corners squared where they meet. Icons come from Font Awesome 3 (`icon-*` classes) at text size, with 24px for emphasis (`.icon-m`).

## Components

### Buttons
Familiar Bootstrap 2 buttons, moving toward flat.
- **Shape:** gently rounded (4px; 5px for large).
- **Default:** a white-to-light-gray button with Ink text and a hairline border. This is the most common button.
- **Primary:** Action Blue, white text. It marks the single main action of a form or header (Save, New record).
- **Danger:** Danger Red, used for delete and confirm-delete only.
- **Large:** the standard size for form-submit bars and header actions (it appears 127 times in the templates).
- **Hover / Focus:** Bootstrap 2 shifts the gradient down to the deeper shade. New flat buttons should shift to the `-deep` color instead and keep a visible focus ring.
- **Legacy one-off:** `.btn-decs`, a gray gradient with right-only rounding attached to the DeCS lookup field. Don't replicate it. New lookup affordances use a default button attached with an input-append.

### Status Labels & Badges
- **Style:** small bold white text on a semantic fill, 3px corners. Badges are 9px pills for counts.
- **House variants:** `label-salmon` (`#fa8072`) and `label-lilac` (`#c8a2c8`) extend the status set for record types. Keep them to existing meanings.

### Content Panel
- **Corner Style:** 5px, squared at the top where it meets the breadcrumb.
- **Background:** Panel White on Paper.
- **Shadow Strategy:** Panel lift (see Elevation & Depth).
- **Border:** 1px Hairline.
- **Internal Padding:** 10px top, 30px bottom, with grid gutters at the sides.

### Inputs / Fields
- **Style:** white field, 1px `#ccc` border, 3px corners, 13px text, 28px tall (`select`).
- **Focus:** the border turns light blue and a soft blue glow appears (see Shadow Vocabulary).
- **Error:** Django errorlists are converted to `alert alert-error` blocks (red text on a pale red fill) above the field.
- **Required:** a red asterisk (`span.mark`, `#e32`) and a bold black label.
- **Help:** labels with help use a dotted underline and a help cursor (`.field_with_help`) and open a help modal.
- **Read-only JSON display:** a gray inset box (`.jsonfield_display`) that opens a context menu for editing.

### Navigation
- **Sidebar:** fixed on the left, BIREME Green Deep, 224px expanded and 56px collapsed (icons only). From top to bottom:
  - The "FI-ADMIN" wordmark (20px, weight 200; "FI" when collapsed), linking to the dashboard.
  - A Dashboard link.
  - The "Information Source" section, which lists the source types.
  - A divided group with Suggestions, Error reports and Reports.
  - For superusers, the expandable "Controlled lists" group and Admin.
  - A pinned footer with the EN/PT/ES switch, the user name and center code, Logout, and the collapse toggle.
  - Items appear only for the user's service roles.
- **Sidebar items:** 36px rows with 4px corners. Each has a 20px Font Awesome icon and a label, and every item has its own icon so the collapsed rail stays readable. Hover adds a 10% white wash. The current page is a white pill with Green Ink bold text (`aria-current="page"`). While collapsed, labels stay in the accessibility tree and appear as a charcoal tooltip on hover or focus. Opening "Controlled lists" while collapsed expands the sidebar first.
- **Mobile bar:** below 768px, a fixed 48px deep-green bar with a menu button and the wordmark. It opens the sidebar as a 264px drawer over a 40% black scrim. Escape or a click on the scrim closes it.
- **Dropdowns:** white menus, and the hovered item is filled Action Blue with white text.
- **Breadcrumb:** a light gradient strip capping the content panel, 11pt.
- **Tabs:** Bootstrap `nav-tabs` split long record forms into methodology groups. The active tab joins the panel surface.
- **Language switch:** EN / PT / ES as a segmented row in the sidebar footer (stacked when collapsed). All three are always visible, and the current one is filled white.

### Dashboard Widgets
- **Style:** flat sections inside the content panel, separated by Rule Soft top borders, not wells or cards. Each head has a 14px bold title and, for on-demand lists, a small default "Check" button on the right.
- **Lists:** rows with a muted 14px icon, a title that wraps, and a right-aligned tabular timestamp in Muted Text, separated by faint rules.
- **States:** a spinner while loading (`aria-busy`), a "No records found" empty line, and a red "Could not load this list. Try again." error line. Results are announced politely.

### Tables
- **Style:** row rules only (1px `#ddd` bottom border, no top border), with 11px vertical cell padding on list tables. `table-striped` and `table-condensed` are the common variants.

### Modals & Alerts
- **Modals:** Bootstrap 2 modals, used heavily (help, dedup, change log, confirmations). The help modal is widened to 750px.
- **Alerts:** inline `alert-error` and `alert-info` are the common variants. Floating toast alerts stack bottom-right at 500px wide.
- **Loading mask:** a full-screen 70% white veil with a centered spinner GIF during form submissions.

### Footer
A 90px Charcoal band. The language-specific BIREME/PAHO/WHO logo sits on the left. Terms and Privacy links in light gray and the app version in Muted sit on the right. The logo and links are mandatory on every authenticated and public page.

## Do's and Don'ts

### Do:
- **Do** keep exactly one white content panel per page on the Paper background, capped by the breadcrumb.
- **Do** use the green family only for the sidebar, the mobile bar and identity bands. Use Action Blue for links and primary actions inside the panel.
- **Do** give every sidebar entry its own distinct icon. The collapsed rail is icons only.
- **Do** build new pieces flat: solid fills, the existing colors and 3–5px radii, with no gradients, inset highlights, or text-shadows.
- **Do** keep Bootstrap 2 structures (nav-tabs, modals, striped tables, wells, input-append) so center staff never relearn the interface.
- **Do** size text containers for PT-BR and ES strings, and pass all copy through `{% trans %}`.
- **Do** report record state with the status colors consistently: published, pending, deleted, draft.

### Don't:
- **Don't** put BIREME Green on buttons or links inside the panel, or Action Blue on bars and bands.
- **Don't** put small white text on the bright BIREME Green (2.5:1). Use BIREME Green Deep.
- **Don't** reintroduce a top navigation bar. Navigation lives in the left sidebar.
- **Don't** add shadows inside the content panel or nest floating cards in it.
- **Don't** introduce new fonts. Helvetica Neue / Arial is the only family.
- **Don't** add new gradient or bevel finishes such as `.btn-decs`. They are legacy to retire, not patterns to extend.
- **Don't** remove or restyle away the footer's BIREME/PAHO/WHO logo and policy links.
- **Don't** use semantic status colors decoratively.
