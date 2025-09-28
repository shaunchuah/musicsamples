# App Package Refactor Plan

## Goals

- Split the monolithic `app` package into domain-aligned Django apps while preserving existing behaviour.
- Reduce coupling between UI views, API views, services, and models so that each app owns its logic, templates, URLs, and tests.
- Establish a shared foundation for cross-cutting utilities that avoids circular imports and makes future extensions easier.

## Target App Layout

| New App | Responsibilities | Notes |
| --- | --- | --- |
| `core` | Shared utilities (pagination mixins, CSV helpers, Azure file adapters), context processors, common templatetags | Replace current `app.utils`/`app.services` fragments. |
| `samples` | Clinical sample CRUD, filters, forms, sample exports, related templates | Moves content from `app/models/clinical.py`, `app/views/sample_views.py`, `app/forms.SampleForm`, etc. |
| `datastore` | File library (uploads, Azure integration, datastore filters, templates) | Extract `DataStore` models, forms, and views. |
| `boxes` | Basic science box inventory, sample types, experimental IDs | Moves `app/models/basic_science.py`, `app/views/box_views.py`, related forms/templates. |
| `analytics` | Aggregations, dashboards, data export endpoints | Pull `analytics_views.py`, analytics templates, pandas-heavy helpers. |
| `study_ids` | Study identifier management, import services, autocomplete | Consolidate `StudyIdentifier` views/routes/services. |
| (optional) `api` | REST/JSON endpoints that should not reside inside template-centric apps | Wrap `api_views.py`, DRF serializers, routers for clearer permission policies. |

## Step-by-Step Plan

1. **Baseline and Inventory**
   - Generate a dependency map of modules within `app/` (e.g. using `python manage.py show_urls`).
   - Document current URL patterns and template paths to ensure parity after the split.
   - Capture database state by noting existing migrations for `app` (list files under `app/migrations/`).

### Step 1 — Baseline Snapshot (2025-09-28)

- **Module Inventory** `app/`
  - Core files: `admin.py`, `choices.py`, `config.py`, `factories.py`, `filters.py`, `forms.py`, `models.py`, `serializers.py`, `services.py`, `utils.py`.
  - Domain folders: `models/` (`basic_science.py`, `clinical.py`, `datastore.py`, `study_ids.py`), `views/` (analytics/api/autocomplete/box/datastore/export/sample/study_id), `urls/`, `tests/`, `templatetags/`.
- **URL Map Summary** (`python manage.py show_urls`)
  - Core feature groups: samples (`/samples/*`, `/filter*`, `/used_samples*`), datastore (`/datastore/*`), study IDs (`/study_id/*`), exports (`/export_*`), analytics/dashboard root (`/`), plus admin + OAuth + debug routes.
  - Observed route namespaces: `home`, `samples`, `datastore`, `study_id`, `export`, `account`, Guardian admin, OAuth2 provider, DRF auth token.
- **Template Directories** (from `templates/`)
  - Feature folders: `samples/`, `datastore/`, `boxes/`, `study_id/`, `datasets/`, `accounts/`.
  - Shared assets: `layouts/`, `includes/`, `emails/`, `barcode/`.
- **Migration Inventory** (`app/migrations/`)
  - 28 numbered migrations present (`0001_initial.py` … `0028_alter_experimentalid_name_and_more.py`).
  - Covers domains: datastore (`0002-0015`), clinical data (`0016-0020`), basic science (`0021-0028`), plus historical apps tracked via `simple_history`.

2. **Create New Django Apps**
   - For each target domain app, run `python manage.py startapp <name>` and move the app into the project root alongside `app/`.
   - Update `config/settings/base.py` `LOCAL_APPS` list by adding the new app names but keep the original `app` entry until migration is complete.
   - Commit the scaffolding to allow incremental refactors.

### Step 2 — App Scaffolding (2025-09-28)

- **Apps created**: `core`, `samples`, `datastore`, `boxes`, `analytics`, `study_ids` using `python manage.py startapp`.
- **Settings update**: Added the new apps to `LOCAL_APPS` ahead of `app` in `config/settings/base.py` to keep legacy components active during migration.
- **Scaffolding conventions**: Inserted header comments in each generated file to document location, purpose, and migration intent per project guidelines.

3. **Establish the Shared `core` Package**
   - Create `core/` app and move infrastructure-level helpers:
     - Pagination helpers, CSV exports, dataframe utilities from `app/utils.py`.
     - Azure storage code from `app/services.py` (`azure_*`, `FileDirectUploadService`).
   - Provide clear module boundaries (e.g. `core/storage/azure.py`, `core/export/csv.py`).
   - Replace direct imports in existing code with the new `core` modules, keeping aliases temporarily available in `app/utils.py` to avoid breaking references during the migration.

### Step 3 — Core Utility Extraction (2025-09-28)

- **Module boundaries**: Created `core/export/csv.py`, `core/dataframe/pivot.py`, `core/history/changes.py`, `core/querysets/studies.py`, and `core/storage/azure.py` plus package `__init__` files with project header comments.
- **Helper relocation**: Moved CSV exports, pandas pivot helpers, historical diff tooling, study queryset filters, Azure upload/download services, and domain import helpers into the new modules.
- **Backwards compatibility**: Converted `app/utils.py` into a shim that re-exports the moved helpers; `app/services.py` now re-exports domain services while call sites migrate.
- **Import updates**: Pointed key views (`app/views/export_views.py`, `app/views/datastore_views.py`, `app/views/sample_views.py`, `app/views/box_views.py`, `app/views/datastore_api_views.py`, `app/views/study_id_views.py`, `app/views/analytics_views.py`) at the new `core` modules as the first adopters.

4. **Extract Models Domain by Domain**
   - **Samples**: Move `Sample`, `ClinicalData`, related choices/constants into `samples/models.py`; copy relevant migrations into `samples/migrations`. Update `ForeignKey` references across the project.
   - **Datastore**: Move `DataStore` into `datastore/models.py`; relocate upload helpers (`file_generate_name`, `file_upload_path`) or keep them in `core.files`.
   - **Boxes**: Move basic science models into `boxes/models.py` with their migrations.
   - Ensure the new app `apps.py` classes set `default_auto_field` consistent with project defaults.
   - Update imports in forms, serializers, services to reference the new modules.

5. **Rewire Migrations Carefully**
   - Decide on migration strategy:
     - Option A: Duplicate existing migration files into the new app directories and adjust `dependencies` to point to the new app labels; keep the history identical so the database schema remains unchanged.
     - Option B: Create squashed “initial” migrations for each new app that represent the current models, then delete the `app` migrations after verifying database alignment.
   - Run `python manage.py makemigrations` for each app to validate that Django recognises the moved models without wanting schema changes.
   - Update any migration references (ForeignKey `to='app.ModelName'`) to the new app labels.

6. **Move Forms, Filters, and Serializers**
   - Relocate `SampleForm`, `CheckoutForm`, `SampleFilter`, DRF serializers into their corresponding app packages (`samples/forms.py`, `samples/filters.py`, `samples/serializers.py`).
   - Adjust import paths across views/tests; provide temporary re-export stubs (e.g. in `app/forms.py`) if needed to maintain backward compatibility while code is updated.

7. **Split Views and URLs**
   - For each new app, create `views/` and `urls.py` modules mirroring the existing `app/views/*` files:
     - `samples/views/__init__.py` for HTML flows and `samples/api/views.py` for DRF endpoints (or move to shared `api` app).
     - `datastore/views.py`, `boxes/views.py`, etc.
   - Update `app/urls/__init__.py` by delegating to the new app URL configs, then progressively remove the old includes once traffic is switched.
   - Ensure namespaced URLs remain unchanged to avoid template breakage.

8. **Reorganise Templates and Static Assets**
   - Move templates into app-specific directories (e.g. `templates/samples/`, `templates/datastore/`), keeping consistent naming with new apps.
   - Update render calls (`return render(request, "samples/sample_list.html", ...)`) to point to the new paths.
   - Extract shared layout/partial templates into `templates/layouts/` or `templates/includes/` under the `core` app if appropriate.

9. **Adjust Settings and Configuration**
   - Once each domain app owns its components, remove the legacy `app` entry from `INSTALLED_APPS`.
   - Update settings that reference the old app label (e.g. permissions, `SAMPLE_PAGINATION_SIZE`, Select2 configs) to use the new app names, possibly grouping them under a dedicated section per app.
   - Review middleware/context processors for any hard-coded references to `app` and relocate them into `core`.

10. **Update Routing and Reverse Lookups**
    - Search for `reverse("...",`, `reverse_lazy`, and template `{% url %}` tags that reference old route names; ensure they align with the new URL namespaces.
    - Maintain compatibility by creating transitional URL patterns that import views from the new apps while keeping historical route names live until templates and external clients are updated.

11. **Refactor Tests and Fixtures**
    - Move `app/tests/samples/` into `samples/tests/`, `app/tests/test_datastore_*` into `datastore/tests/`, etc.
    - Centralise shared fixtures (user factory, permissions) under `core/tests/` or `tests/common/` to avoid circular imports.
    - Update pytest `conftest.py` locations and adjust imports for the new app labels.

12. **Data Migration & Backward Compatibility Review**
    - Run full test suite and targeted smoke tests after each domain extraction.
    - Verify admin registrations (`app/admin.py`) are split across the new apps (`samples/admin.py`, etc.).
    - Ensure Django permissions and Guardian object permissions are re-assigned with the new app labels to prevent access regressions.

13. **Cleanup the Legacy `app` Package**
    - After all domains are migrated and tests pass, remove the now-empty modules from the `app` package.
    - Delete redundant re-export stubs, update documentation, and adjust README sections referencing the old app structure.
    - Create a final migration, if necessary, to clear out any stale ContentTypes referencing `app` models.

14. **Deployment & Monitoring**
    - Deploy to a staging environment, checking for migration conflicts and verifying Azure file operations still function through the `core` abstractions.
    - Monitor logs for missing import errors, template resolution issues, or permission problems.
    - Once stable, tag the release and communicate the new app boundaries to the team.

## Tracking & Communication

- Record progress in this file per domain app extraction.
- Update developer documentation (`docs/` or `AGENTS.md`) with the new directory layout and guidelines for adding future features.
- Encourage contributors to follow the new boundaries when adding models/views/tests.
