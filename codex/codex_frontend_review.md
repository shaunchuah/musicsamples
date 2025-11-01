<!-- codex_frontend_review.md -->
<!-- Frontend UI review notes covering current state and modernization ideas. -->
<!-- Exists to document Codex's assessment at the user's request. -->
# Frontend UI Review

## Current Experience

- Relies on Black Dashboard's Bootstrap 4 skin; visual language feels dated with dense gradients (`btn btn-fill`) and limited white space in primary pages such as `templates/samples/sample_list.html` and `templates/samples/sample_filter.html`.
- Tables dominate the layout without contextual framing; the 22-column grid in `templates/samples/includes/sample_table.html` overflows on smaller screens despite the `table-responsive` wrapper, forcing awkward horizontal scrolling and reducing readability.
- Action buttons use `float-*` utilities (e.g., `float-lg-right`) that collapse into stacked blocks on mobile, leaving inconsistent spacing and alignment.
- Forms have minimal labelling support: the search input lacks placeholder guidance, the checkbox for "Include used samples" is visually detached, and advanced filter controls render as raw select boxes without helper text or grouping.
- Navigation elements inherit Black Dashboard defaults; inactive menu items, combined with a large sidebar logo image, consume significant vertical space and slow scanning.

## Modernization Opportunities

- **Design system refresh**: Consider replacing Black Dashboard with a lighter Bootstrap 5 (or DaisyUI/Tailwind) kit, enabling consistent spacing, updated form controls, and native utility classes (`gap`, `flex` alignment) without custom floats.
- **Responsive table strategy**: Introduce a condensed summary view for narrow screens (cards, column toggles, or `data-*` driven accordions). Combine low-value columns (e.g., biomarker results) into collapsible drawers, or provide export-only data for rarely used fields.
- **Action hierarchy**: Group primary/secondary actions with flex utilities instead of floats. Add icons + text consistently, use `btn-outline` variants for secondary actions, and surface destructive actions (e.g., "Used") via dropdown menus to reduce inline clutter.
- **Form usability**: Add descriptive placeholders/ARIA hints, inline validation messaging, and convert the advanced filter form into grouped sections with headings (Study Details, Clinical Data, etc.). Date/time filtering (`sample_datetime`) would benefit from a calendar picker (`flatpickr` or Bootstrap Datepicker).
- **Feedback patterns**: Replace stacked Bootstrap alert blocks in `templates/includes/messages.html` with toast notifications or a single, dismissible alert container aligned with the navbar, keeping page content from shifting.
- **Visual polish**: Swap the raster sidebar logo for an SVG, shrink its footprint, and add a compact header branding area. Leverage CSS variables for theming and adopt a lighter background (`white-content` currently forces light mode but retains dark accents).

## Refactoring Suggestions

- Extract the duplicated tablesorter initialization script from both sample pages (`templates/samples/sample_list.html`, `templates/samples/sample_filter.html`) into a dedicated static JS module (e.g., `static/assets/js/sample-table.js`) and load it conditionally via `block javascripts`.
- Centralize search/filter forms using a reusable partial so that button layouts, helper text, and checkbox styling stay in sync across list and filter views.
- Simplify template logic in `templates/samples/includes/sample_table.html` by moving repeated inline `if` checks into template filters or model properties (e.g., `sample.display_study_group`) to reduce template noise and improve maintainability.
- Consolidate the pagination rendering to accept configuration (page size, label text) instead of hard-coding ranges in `templates/layouts/pagination.html`; this will ease future upgrades to component libraries.
- Audit static asset loading: defer non-critical scripts (tablesorter, typeahead) and drop unused vendor bundles from `templates/includes/scripts.html` to speed up first paint.

### Quick Wins

- Tidy button spacing with Bootstrap flex utilities (`d-flex flex-wrap gap-2`) and replace `float-lg-right`.
- Add badges or chips for categorical values (Sample Type, Used status) to increase scanability.
- Use sticky headers (`position: sticky`) or row striping to keep column labels visible on long tables.
- Provide an empty-state component with actionable guidance when no samples are returned, instead of a single text row.
- Enable tooltip titles on icon-only links (`View`, `Edit`, `Used`) to aid accessibility and keyboard navigation.

### Open Questions

1. Which columns do lab users rely on most day-to-day? Prioritizing those can drive a cleaner, card-based responsive view.
2. Are there plans to expose analytics widgets on the dashboard? Aligning the visual language now will ease integration of future charts.
3. Is dark mode valuable to your user base? If so, consider toggles that pair with CSS variables rather than the hard-coded `white-content` class.

---
Feel free to reach out with prioritization guidance so the next iteration targets the highest-impact improvements first.
