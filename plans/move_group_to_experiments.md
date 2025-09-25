# Move `basic_science_group` to `ExperimentalID`

## Progress Snapshot

- ✅ `ExperimentalID` owns `basic_science_group` without a model-level default; migration seeds existing rows with `other` only during the schema change.
- ✅ Box helpers, templates, admin, and CSV/search/filter flows now read groups from linked experiments.
- ✅ Experiment creation (form + AJAX) exposes the group field and surfaces it in client updates.
- ✅ Regression tests cover searching/filtering by group alongside form behaviour; targeted pytest suite passes.

## Next Actions

1. **Communication**
   - Confirm stakeholders are comfortable marking legacy experiments as `Other` and note any manual clean-up expectations.
   - Capture the workflow change (experiment-owned group field) in release notes or internal docs.
2. **Follow-up QA**
   - Spot-check UI flows in a browser once deployed (box create/edit, experiment modal, filter/search, CSV export) to ensure styling changes look right.
   - Monitor for additional data integrity tooling requests (e.g., reports of experiments spanning multiple groups).
