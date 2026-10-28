# Sidebar menu and dashboard polish

## Sidebar (replaces the top navbar)
- `src/templates/menu.html`: rebuilt as a fixed left sidebar (`#app-sidebar`). It keeps every role/center gate of the old navbar.
  - New Dashboard link.
  - Each entry has its own Font Awesome 3 icon.
  - "Controlled lists" is an expandable group (superusers).
  - Footer: EN/PT/ES switch, user + center code, Logout, collapse toggle.
- `src/static/js/sidebar.js` (new):
  - Collapse to a 56px icon rail, remembered in localStorage.
  - Tooltips while collapsed.
  - Active-page highlight with `aria-current`.
  - Group toggle that expands the sidebar first when collapsed.
  - Off-canvas drawer on screens under 768px (scrim, Escape, focus return).
- `src/templates/base.html`: an inline head script restores the collapsed state before first paint; `sidebar.js` is included.
- `src/static/css/screen.css`:
  - Removed the obsolete `.navbar*`, `#menu i` and dropdown logout rules.
  - Added the sidebar, mobile bar and frame offset styles, scoped with `body:has(.app-sidebar)`, so pages without the menu (popups, login) are unchanged.
  - The sidebar uses deep BIREME green `#00704f`: white text reaches 6:1, versus 2.5:1 on `#00ba8b`.
  - The footer wraps instead of clipping at narrower content widths.

## Dashboard polish
- `src/templates/dashboard/index.html`:
  - Fixed `{% block "title" %}` → `{% block title %}`, so the page title now reads "Dashboard | …".
  - Added a breadcrumb.
  - Header matches list pages (h3 plus a meta line).
  - `row` → `row-fluid`: fixed-width spans broke next to the sidebar.
  - Wells replaced by flat, rule-separated sections; "check" links are now buttons.
  - Live regions, `aria-busy` while loading, and a new error state.
- `src/templates/dashboard/widget_*.html`: lists with empty states, and timestamps in muted tabular text using `SHORT_DATETIME_FORMAT`.

## i18n / tooling
- New strings translated in `locale/pt_BR` and `locale/es`: "Main menu", "Open menu", "Collapse menu", "Expand menu", "Could not load this list. Try again."
- Recompiled the `.mo` files.
- New Makefile target `dev_compile_translations`.

## Design docs
- `DESIGN.md` and `.impeccable/design.json` updated: sidebar navigation, new color tokens (green deep/ink, sidebar mint, muted text), and the dashboard widget pattern.

## Verification
- Rendered with a fake user (no DB writes) and screenshotted in headless Chromium:
  - 1440 EN expanded; 1440 PT collapsed; 1024 error state; 390 PT mobile, closed and open.
  - A scripted click test covered collapse, tooltip and group behavior.
- `make dev_check` clean; `make dev_test_app app=dashboard` passes 5/5.
