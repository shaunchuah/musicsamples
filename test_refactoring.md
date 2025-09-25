# Test Suite Refactoring Plan

## Current Pain Points

- `app/tests/test_box_views.py` is 1,211 LOC and mixes detail, list, CRUD, function-based, and experimental ID flows, making navigation and focused review hard.
- `app/tests/test_urls.py` is 506 LOC covering every route across apps, so adding a route requires touching an oversized file with unrelated assertions.
- `app/tests/test_views.py` is 313 LOC combining pytest-style functions with Django `TestCase`, multiple fixtures, and cross-cutting sample workflows in one place.
- Permission and authentication helpers are redefined per class instead of shared fixtures, increasing duplication and setup overhead.
- Naming is largely view-driven; grouping by domain (boxes, samples, datasets, users) would align tests with feature ownership and reduce merge conflicts.

## Refactoring Goals

- Improve readability by scoping each file to a single feature slice or view type.
- Centralize common fixtures/helpers so authentication, permissions, and factories are reused.
- Maintain granular pytest collection so failures isolate quickly and parallel runs stay efficient.
- Prepare the suite for future feature-specific regression tests without creating mega-files again.

## Target Directory Layout (app/tests)

```
app/tests/
    conftest.py                   # shared fixtures (auth user, permission helper, factories)
    helpers.py                    # optional shared assertion helpers
    boxes/
        __init__.py
        conftest.py               # box-specific factories/fixtures if needed
        test_basic_science_box_detail.py
        test_basic_science_box_list.py
        test_basic_science_box_create.py
        test_basic_science_box_update.py
        test_basic_science_box_delete.py
        test_box_function_views.py     # filter/search/export endpoints
        test_experimental_id_api.py    # create endpoint returning JSON
        test_experimental_id_views.py  # list/detail/update/delete views
    samples/
        __init__.py
        conftest.py
        test_sample_create.py
        test_sample_detail.py
        test_sample_edit.py
        test_sample_checkout.py
        test_sample_search.py
        test_sample_barcode.py
    urls/
        __init__.py
        test_core_urls.py          # home, analytics, export, etc.
        test_sample_urls.py
        test_box_urls.py
        test_dataset_urls.py
        test_user_urls.py
    services/
        __init__.py
        test_study_identifier_import.py
    pagination/
        __init__.py
        test_pagination.py         # optional move if further files grow
```

## Box View Split (1,211 LOC → feature modules)

1. **Create `app/tests/boxes` package** with `__init__.py` + `conftest.py` and move shared `PermissionHelperMixin` into pytest fixtures (`user_with_perm`, `grant_perm`).
2. **Detail view**: migrate `BasicScienceBoxDetailViewTest` to `test_basic_science_box_detail.py`; switch to pytest style where possible, keep RequestFactory tests where valuable.
3. **List view**: move `BasicScienceBoxListViewTest` to `test_basic_science_box_list.py`; reuse shared fixtures for login + perms.
4. **Create/Update/Delete**: group CRUD tests into dedicated modules (or a single `test_basic_science_box_crud.py` if duplication is minimal) to keep each under ~200 LOC.
5. **Function-based endpoints** (`box_search`, `export_boxes_csv`, filters): relocate to `test_box_function_views.py`, convert repeated CSV assertions into helper utilities.
6. **Experimental ID flows**: place class-based views in `test_experimental_id_views.py` and API creation tests in `test_experimental_id_api.py`; share fixtures for factories, patching, and permission grants.
7. Update imports to use relative paths (`from ..conftest import user_with_perm`) and ensure pytest auto-discovers (`tests` prefix maintained).

## Sample View Split (current `test_views.py`)

1. Extract reusable pytest fixtures (`auto_login_user`, `create_user`, `other_user`) into `samples/conftest.py` so modules stay lean.
2. Break down by workflow:
   - `test_sample_create.py`: `test_add_sample_page`, `test_add_sample_post`.
   - `test_sample_detail.py`: detail + processing time assertions.
   - `test_sample_edit.py`: edit flows.
   - `test_sample_checkout.py`: checkout/used transitions.
   - `test_sample_search.py`: search behaviour including query/no-query cases.
   - `test_sample_barcode.py`: barcode and related endpoints currently in the same file (confirm coverage before moving).
3. Confirm pytest fixtures still resolve globally (pytest searches parent `conftest.py` files automatically).
4. Consider migrating Django `TestCase` usage to pure pytest requests (client fixture) for consistency.

## URL Coverage Split

1. Introduce `app/tests/urls` package with modules grouped by responsible app.
2. `test_core_urls.py`: routes defined in `app/views` (home, analytics, reference, filter, exports).
3. `test_sample_urls.py`: sample CRUD, barcode, autocomplete endpoints.
4. `test_box_urls.py`: boxes + experimental IDs (mirrors `boxes/` directory).
5. `test_dataset_urls.py` / `test_user_urls.py`: import from respective apps to keep ownership clear.
6. Replace generic `TestUrls` class with pytest parameterization (`pytest.mark.parametrize`) to reduce repetition and file length.

## Shared Fixture Strategy

- Root-level `app/tests/conftest.py` exposes fixtures for authenticated user, staff user, API client, CSV assertion helpers, and permission grants.
- Domain-specific `conftest.py` (e.g. `boxes/`) can add factories for frequent objects (`BasicScienceBoxFactory`, `ExperimentalIDFactory`).
- Migrate helper mixins (`PermissionHelperMixin`) to fixtures returning callables to align with pytest idioms.
- Extract duplicated CSV/export assertions into helper functions in `app/tests/helpers.py`.

## Implementation Phases

1. **Scaffolding**
   - Create new package directories, `__init__.py`, and placeholder `conftest.py` files.
   - Move shared fixtures from `test_views.py` and `test_box_views.py` into new `conftest.py` iteratively.

2. **Box Tests Migration**
   - Move Basic Science box detail/list tests first (lowest coupling) and ensure imports resolve.
   - Migrate CRUD + function-based tests, adjusting fixtures and helper utilities.
   - Finalize experimental ID modules; run targeted `pytest app/tests/boxes` after each move.

3. **Sample Tests Migration**
   - Incrementally move workflows, deleting migrated sections from `test_views.py` until file is empty, then remove the original module.
   - Adopt parametrization where multiple tests differ by endpoint or expected template.

4. **URL Tests Migration**
   - Create new files and progressively move route groups, leveraging shared parameter lists.
   - Once all sections move, delete `test_urls.py` and ensure `pytest app/tests/urls` passes.

5. **Cleanup & Follow-up**
   - Update any `pytest.ini` or coverage configs if they target file names explicitly (none observed, but verify).
   - Run full `pytest` to confirm discovery order is unchanged.
   - Monitor coverage reports to ensure no accidental drops.

## Risks & Mitigations

- **Pytest discovery gaps**: mitigate by keeping filenames prefixed with `test_` and ensuring `__init__.py` exist in new directories.
- **Fixture import loops**: maintain root-level fixtures minimal; keep domain fixtures in child `conftest.py` files that only import factories, not view modules.
- **Large diffs**: migrate in small commits per module move to keep reviews manageable.
- **Behavioural regressions**: run targeted pytest subsets during migration; avoid rewriting assertions unless necessary.

## Suggested Verification

- After each module move: `pytest app/tests/boxes/test_basic_science_box_detail.py` (or equivalent path).
- After completing each phase: `pytest app/tests/boxes`, `pytest app/tests/samples`, then `pytest app/tests`.
- Final gate: full `pytest` run to confirm suite health and coverage parity.
