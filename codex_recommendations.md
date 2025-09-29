# Structural & Organisational Recommendations

## 1. Split the monolithic `app` package into bounded Django apps

- The current `app` package mixes unrelated concerns (samples, boxes, analytics, datastore, study IDs, exports) under one app directory, which makes settings, migrations, and permissions harder to reason about (`app/views/sample_views.py`, `app/views/datastore_views.py`, `app/urls/__init__.py`).
- Introduce domain-focused Django apps (e.g. `samples`, `datastore`, `analytics`, `references`) and move their models, forms, urls, and templates accordingly. Keep shared helpers in a new `common` app or package to avoid circular imports.
- As part of the split, scope app-level settings (`INSTALLED_APPS`, permissions) and tests to the new apps so each module owns its configuration and fixtures.

## 2. Consolidate duplicated view-layer patterns

- Multiple function-based views reimplement the same pagination, filtering, and CSV export patterns (`app/views/sample_views.py:27`, `app/views/datastore_views.py:73`, `app/views/datastore_views.py:118`).
- Introduce class-based views or reusable mixins (e.g. `PaginatedFilterView`) that handle the boilerplate for pagination/querystring reconstruction and CSV export endpoints. This will shrink view modules and centralise behaviour changes.
- Keep API views separate from template-rendering views. Today REST endpoints and HTML handlers live side-by-side in the same module (`datasets/views.py`), which complicates authentication/permission policies.

## 3. Separate dataset orchestration concerns

- Dataset HTML views, API serializers, and access tracking logic live in a single module (`datasets/views.py`), making it harder to evolve API contracts independently of the dashboard.
- Split into `datasets/api/views.py` and `datasets/web/views.py`, and add a thin service layer to encapsulate history tracking and export logic (`datasets/utils.py`) so both entry points reuse the same orchestration code.

## 4. Decouple Azure storage dependencies for local workflows

- Local settings force Azure Blob Storage for the default file backend and expect credentials to exist (`config/settings/local.py`), while upload utilities reach directly into Azure SDK calls (`core/services/storage.py`, `core/services/uploads.py`). Contributors without Azure secrets can’t run uploads or tests without stubbing those settings.
- Introduce a storage abstraction that delegates to Django’s `default_storage` by default, and only swap in Azure-specific behaviour when the related environment variables are present. Provide a filesystem-backed default for local/test runs so developers can exercise file flows without cloud credentials.
