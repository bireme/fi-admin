# Remove unused styles from screen.css

`src/static/css/screen.css` went from 2009 to about 1765 lines. Only selectors that match nothing in the app were removed. No rendered style changed.

## Method
- Pulled every class and id from the stylesheet's selectors and searched for each one in `src/templates`, `src/static/js` (vendored plugins included), Python view, form and templatetag code, and the deform/Django widget templates. Other stylesheets, `htmlcov`, locale files and migrations were not counted as usage.
- Checked classes and ids that are built at runtime, so they were kept:
  - `label-{{ label_color }}` in `utils/templatetags/app_filters.py` (`lilac`, `salmon`, `inverse`, `info`, `success`, `warning`, `important`)
  - `id="field_{{ field.name }}"` (`#field_LILACS_indexed`, `#field_CVSP_resource`, `#field_reviewed`)
  - `class="row_{{ field.name }}"` (`.row_order`, `.row_act_apparatus`)
  - `alerttype = "alert-success"` in `main/views.py`
  - `.add-on`, used by the bootstrap-datepicker component
  - `.modal-backdrop`, injected by Bootstrap JS

## Removed
- Legacy layout leftovers: `#push`, `.confirm_change`, `.block` / `.block .line`, `#help` / `#help h3`, `.item` and its children, `.count`, `div.onlineresource div.check`, `#indexed_database`.
- The Django admin filter-horizontal clone: `.stacked`, `.selector-available`, `.selector-filter`, `.selector-chooser`, `.selector-chosen`, `.filtered`.
- The multiselect widget: `#multiselect`, `#multiselect_to`, `.multiselect_buttons`, `.multiselect_label`.
- Thesaurus selectors with no match: `.identifierdesc`, `.abbrev`, the `.conceptlistdesc` and `.conceptlistqualif` classes (the templates use them only as ids), `.concept_name`, `.td-l`, `.previousindexinglistdesc`, `.treenumberslistqualif`, `.casn1`, `.category-row`, `.color_status`, and the stray `th td` selectors, which can never match.
- Unused Bootstrap 2 overrides: `.text-error`, `.text-success`, `.text-info`, `.text-warning`, `.btn-inverse`, `.input-prepend`, `.nav-pills`, `.nav-list`, `.table-bordered`, every `.badge-*` except `.badge-info`, and `.progress .bar`.

## Tidied
- Merged the three `.input-append .add-on` rules into one, and merged `#footer`'s height into its main rule.
