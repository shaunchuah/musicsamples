# Structural & Organisational Recommendations

## 1. Split the monolithic `app` package into bounded Django apps

- The current `app` package mixes unrelated concerns (samples, boxes, analytics, datastore, study IDs, exports) under one app directory, which makes settings, migrations, and permissions harder to reason about (`app/views/sample_views.py`, `app/views/datastore_views.py`, `app/urls/__init__.py`).
- Introduce domain-focused Django apps (e.g. `samples`, `datastore`, `analytics`, `references`) and move their models, forms, urls, and templates accordingly. Keep shared helpers in a new `common` app or package to avoid circular imports.
- As part of the split, scope app-level settings (`INSTALLED_APPS`, permissions) and tests to the new apps so each module owns its configuration and fixtures.

## 2. Consolidate duplicated view-layer patterns

- Multiple function-based views reimplement the same pagination, filtering, and CSV export patterns (`app/views/sample_views.py:27`, `app/views/datastore_views.py:73`, `app/views/datastore_views.py:118`).
- Introduce class-based views or reusable mixins (e.g. `PaginatedFilterView`) that handle the boilerplate for pagination/querystring reconstruction and CSV export endpoints. This will shrink view modules and centralise behaviour changes.
- Keep API views separate from template-rendering views. Today REST endpoints and HTML handlers live side-by-side in the same module (`datasets/views.py`), which complicates authentication/permission policies.

## 3. Refactor service and utility layers into cohesive modules

- `app/services.py` contains unrelated responsibilities: Azure Blob storage helpers, file upload coordination, and Study Identifier import logic (`app/services.py:14-200`).
- `app/utils.py` likewise blends CSV export, queryset filtering, and pandas dataframe shaping (`app/utils.py:11-200`).
- Break these into purpose-driven modules, e.g. `services/storage.py`, `services/imports.py`, and `utils/export.py`/`utils/dataframes.py`. Define clear public interfaces so other apps consume narrowly-scoped helpers, making it easier to swap storage backends or extend import pipelines.

## 4. Align templates with their owning app and introduce shared layout components

- Many templates live at the project root (`templates/management.html`, `templates/reference.html`) despite belonging to specific domains handled in the `app` package, increasing coupling between apps and template names.
- Mirror the Django app structure inside `templates/` so that URLs in, for example, the future `samples` app resolve to `samples/…` templates. Reserve the project-level `templates/` root for global layouts (`layouts/`), partials (`includes/`), and error pages.
- Extract repeated dashboard scaffolding (navigation, cards) into reusable includes or a base template so new apps can inherit consistent layouts without copy/paste.

## 5. Clarify settings layering and environment configuration

- Base settings import `.env` unconditionally (`config/settings/base.py`), yet production/local modules override numerous environment-specific values. Move environment-only defaults (e.g. debug emails, storages, Azure credentials) into `local.py`/`production.py` and guard `.env` loading so production can rely on environment variables.
- Consider adopting `config/settings/__init__.py` that selects a settings module via `DJANGO_SETTINGS_MODULE` and document the expected environment variables. This keeps the base layer environment-agnostic and eases deployment automation.

## 6. Separate dataset orchestration concerns

- Dataset HTML views, API serializers, and access tracking logic live in a single module (`datasets/views.py`), making it harder to evolve API contracts independently of the dashboard.
- Split into `datasets/api/views.py` and `datasets/web/views.py`, and add a thin service layer to encapsulate history tracking and export logic (`datasets/utils.py`) so both entry points reuse the same orchestration code.

## 7. Strengthen test organisation after restructuring

- Tests currently mirror the monolithic layout (`app/tests/...`). As you extract domain apps, create per-app `tests/` packages and move fixtures/factories alongside domain code (`datasets/factories.py`, `app/factories.py`).
- Promote shared fixtures (e.g. user factories, permission helpers) into a project-level `tests/common/` module to avoid cross-app imports.
