<!-- codex/plans/v3-backend-separation.md -->
<!-- ExecPlan to decouple the Django v3 API for the Next.js frontend and isolate it from legacy templates. -->
<!-- Exists to guide building a headless-ready backend surface while keeping the existing Django UI stable. -->

# Decouple V3 API Backend for Next.js Frontend

This ExecPlan is a living document. Maintain it in accordance with codex/PLANS.md and update `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` as work continues.

## Purpose / Big Picture

Move the project toward a clean frontend/backend split by introducing a dedicated v3 API surface tailored for the Next.js app in `frontend/`. After implementation, developers should be able to run Django as a headless API (without serving HTML templates) while the Next.js client uses stable endpoints for authentication (login/refresh/blacklist handled inside `api_v3`), user profile retrieval, sample listing/detail, and CSV export. Legacy Django templates must continue to function during the transition, even if that means duplicating some API endpoints under `api_v3`.

## Progress

- [x] (2025-12-18 11:34Z) Captured current architecture and authored initial ExecPlan skeleton.
- [x] (2025-12-18 11:57Z) Created `api_v3` app scaffolding, routed v3 endpoints through it, duplicated auth/profile endpoints for the frontend, and re-exported legacy imports.
- [ ] Establish dedicated `api_v3` Django app structure (urls, views, serializers) separate from template views. (remaining: serializer relocation if needed)
- [ ] Migrate sample list/detail/create/update endpoints into the new module and keep backward-compatible routing. (remaining: consider moving serializers/filters if desired)
- [ ] Add user-profile and auth helper endpoints aligned with Next.js cookie/JWT flow. (remaining: finalize any additional auth surfaces beyond SimpleJWT + legacy login)
- [ ] Add export-friendly list endpoint or helper for CSV aggregation with explicit limits and pagination defaults.
- [ ] Harden settings (CORS, DRF defaults) for headless use and document environment needs.
- [ ] Add/extend pytest coverage for new endpoints and filters; ensure existing tests stay green.
- [x] (2025-12-18 12:05Z) Verified auth/profile and sample v3 tests: `pytest api_v3/tests/test_auth_and_users.py app/tests/test_api_v3_samples.py` (all pass).

## Surprises & Discoveries

- Observation: Local venv points to a missing interpreter (`python3.11`), causing `pytest` to fail with `bad interpreter`.
  Evidence: `zsh:1: .../venv/bin/pytest: bad interpreter: .../python3.11: no such file or directory` when running `source venv/bin/activate && pytest api_v3/tests/test_auth_and_users.py app/tests/test_api_v3_samples.py`.
- Observation: After switching to `.venv`, auth tests required hashed passwords; updating `UserFactory` to set passwords via `set_password` fixed SimpleJWT login for `/api/v3/auth/login`.
  Evidence: `pytest api_v3/tests/test_auth_and_users.py app/tests/test_api_v3_samples.py` now passes (5 tests), whereas prior run returned 401 on token obtain.

## Decision Log

- Decision: Use a dedicated `api_v3` Django app to house DRF routers, views, and serializers for the Next.js client, rather than adding more to `app/views` or legacy URLs.
  Rationale: Keeps API concerns isolated, allows gradual migration, and avoids coupling with template-specific logic.
  Date/Author: 2025-12-18 / Codex
- Decision: Place all frontend-facing auth/user API endpoints inside `api_v3` (including login/refresh/blacklist/profile), duplicating any shared endpoints as needed to avoid breaking legacy template consumers.
  Rationale: Guarantees the Next.js client has a single, self-contained API surface while the old UI continues to function unmodified.
  Date/Author: 2025-12-18 / Codex
- Decision: Expose SimpleJWT endpoints at `/api/v3/auth/*` and retain the legacy email/password login flow as `/api/v3/auth/legacy-login` while leaving original `/api/token/*` untouched.
  Rationale: Provides the frontend with a consistent v3 auth namespace without breaking existing consumers that rely on older paths.
  Date/Author: 2025-12-18 / Codex

## Outcomes & Retrospective

To be updated after milestones; summarize what works, what remains, and any lessons for future migrations.

## Context and Orientation

The Django project currently mixes HTML template views and DRF APIs inside `app/`. `config/urls.py` includes `app/urls/__init__.py`, which wires web routes plus two DRF routers: `app/urls/api.py` (legacy endpoints) and `app/urls/api_v3.py` (currently only `SampleV3ViewSet`). Authentication uses `rest_framework_simplejwt` at `/api/token/`, `/api/token/refresh/`, and `/api/token/blacklist/` (defined in `users/urls.py`). The Next.js prototype in `frontend/` proxies requests to `/api/v3/samples/` for list/detail/export and `/api/v3/users/me/` for profile data, and relies on HTTP-only JWT cookies set by its own API routes. DRF defaults enforce `IsAuthenticated`, with CORS allowing localhost:3000 and production origins. There are no dedicated backend-only settings; HTML and API share middleware and installed apps. To support the frontend-only surface, we will duplicate shared auth/profile endpoints inside `api_v3` without removing the originals used by templates.

## Plan of Work

Create a dedicated `api_v3` Django app that exposes all endpoints the Next.js client needs while keeping existing routes alive during migration. Refactor minimally: reuse existing models, filters, paginators, and serializers where possible, moving them only when it reduces coupling or duplication. For endpoints shared with the legacy templates (notably auth and user profile), duplicate implementations inside `api_v3` so the frontend can rely solely on the new namespace. Avoid database schema changes.

Milestone 1: Baseline and target definition. Audit current v3 routes, serializers, filters, and DRF settings; map them to the Next.js expectations (samples list/detail/create/update, CSV-friendly listings, user profile, JWT auth). Capture any gaps (e.g., missing fields, filtering needs, export performance constraints) and add tests that describe the current behavior.

Milestone 2: Introduce `api_v3` app skeleton. Add `api_v3/apps.py`, `api_v3/urls.py`, and per-area view modules (e.g., `api_v3/views/samples.py`, `api_v3/views/users.py`, `api_v3/views/auth.py`) plus serializer modules if splitting improves clarity. Register the app in `INSTALLED_APPS`. Wire `config/urls.py` to include `api_v3/urls.py` under `/api/v3/`. Keep `app/urls/api_v3.py` temporarily delegating to the new router to avoid breaking existing consumers.

Milestone 3: Sample endpoints. Move or wrap `SampleV3ViewSet` into `api_v3/views/samples.py`, reusing `SampleV3Serializer`, `SampleV3DetailSerializer`, `SampleV3Filter`, and `SamplePageNumberPagination`. Preserve ordering, filtering, and audit stamping (`perform_create`, `perform_update`). Ensure list endpoints default to excluding `is_used=True` unless requested, and accept `include_used=true` for completeness. Add explicit pagination defaults suitable for CSV aggregation (e.g., allow `page_size` up to a safe ceiling). Update OpenAPI tags to keep docs coherent.

Milestone 4: User and auth helpers. Provide `GET /api/v3/users/me/` via a DRF view in `api_v3/views/users.py` that mirrors `users.api_views.CurrentUserAPIView` but lives in the new namespace. Duplicate the JWT auth endpoints (`/api/v3/auth/login`, `/api/v3/auth/refresh`, `/api/v3/auth/blacklist` or similar) inside `api_v3` wrapping the SimpleJWT views so the frontend can rely solely on this namespace. Retain the original `/api/token/*` and `/api/v3/users/me/` in legacy locations for template consumers. Document any CORS/CSRF considerations for cookie-based clients.

Milestone 5: Export support. Either expose a lightweight CSV endpoint or document how the existing paginated list supports export (the Next.js app currently paginates and builds CSV client-side). Guarantee stable field names and numeric/boolean normalization in `SampleV3Serializer` to avoid `null` vs empty-string surprises. Consider adding a throttled `?format=csv` or `?page_size` cap to keep server load reasonable; codify behavior in tests.

Milestone 6: Settings hardening. Confirm CORS and DRF defaults cover the decoupled frontend; set `REST_FRAMEWORK` pagination defaults if needed, and ensure `SPECTACULAR_SETTINGS` exposes the new routes. Avoid changing database settings. Add minimal middleware adjustments only if required for API-only responses (e.g., disabling template reload middleware in prod is optional).

Milestone 7: Tests and docs. Extend pytest coverage (e.g., `api_v3/tests/`) to cover sample CRUD, filtering, pagination caps, audit stamping, and `/api/v3/users/me/` auth behavior. Keep existing tests (like `app/tests/test_api_v3_samples.py`) passing; if moved, relocate with equivalent assertions. Update README or a short API usage note (if needed) to point Next.js developers to the new endpoints and headers.

## Concrete Steps

- Workdir: /Users/chershiongchuah/Developer/musicsamples
  Create the new app scaffolding and wire URLs while keeping legacy routes intact.
- Workdir: /Users/chershiongchuah/Developer/musicsamples
  Port `SampleV3ViewSet` and related serializers/filters into the new app; ensure router registration under `/api/v3/` and maintain a shim from `app/urls/api_v3.py` if necessary.
- Workdir: /Users/chershiongchuah/Developer/musicsamples
  Add `/api/v3/users/me/` view in the new app, mirroring existing serializer behavior; confirm JWT endpoints remain reachable for the Next.js auth proxy.
- Workdir: /Users/chershiongchuah/Developer/musicsamples
  Add or document export-friendly behavior (page size caps, CSV endpoint if implemented) and ensure response fields match frontend expectations.
- Workdir: /Users/chershiongchuah/Developer/musicsamples
  Update settings (CORS/DRF/OpenAPI) only as needed to support the decoupled frontend without altering database config.
- Workdir: /Users/chershiongchuah/Developer/musicsamples
  Tests: `source venv/bin/activate && pytest app/tests/test_api_v3_samples.py` plus new `api_v3` test modules to cover list/detail/create/update, filtering, and `/api/v3/users/me/`.

## Validation and Acceptance

Acceptance is behavioral. With the Django server running locally on :8000, a JWT-bearing client should be able to:
1) `GET /api/v3/samples/?page_size=100` returns paginated results with `study_identifier`, labels, and default exclusion of `is_used=True` unless `include_used=true` is set.
2) `GET /api/v3/samples/<sample_id>/` returns the detailed serializer with history metadata.
3) `POST /api/v3/samples/` and `PATCH /api/v3/samples/<sample_id>/` stamp `created_by` and `last_modified_by` with the authenticated user.
4) `GET /api/v3/users/me/` returns the authenticated user profile and groups.
5) Export pathway: either `GET /api/v3/samples/?page_size=1000` (capped) supports the Next.js CSV aggregator without errors, or a dedicated CSV endpoint returns the same fields.
6) pytest suite passes, including new `api_v3` tests and existing v3 sample tests.

## Idempotence and Recovery

All steps are additive and configuration-only; no database migrations are planned. Re-running setup commands is safe. If routing changes cause regressions, re-enable the legacy `app/urls/api_v3.py` include while fixing the new app. Keep environment variables unchanged; no data mutations beyond CRUD operations in tests.

## Artifacts and Notes

- Key references: `app/views/v3_api_views.py`, `app/serializers.py` (SampleV3 serializers), `app/filters.py` (SampleV3Filter), `app/pagination.py` (SamplePageNumberPagination), `users/api_views.py` (current user endpoint), `config/urls.py` (routing).
- Frontend expectations: Next.js proxies to `/api/v3/samples/` and `/api/v3/users/me/`, authenticates via `/api/token/` and `/api/token/refresh/`, and performs CSV export by paginating sample results.

## Interfaces and Dependencies

- Django app: `api_v3` (new), added to `INSTALLED_APPS`.
- URLs: `config/urls.py` includes `path("api/v3/", include("api_v3.urls"))`; legacy `app/urls/api_v3.py` can delegate to the new router for compatibility.
- Views: `api_v3/views/samples.py` exposes a DRF `ModelViewSet` equivalent to `SampleV3ViewSet`; `api_v3/views/users.py` exposes `CurrentUserAPIView`-like view at `/users/me/`; `api_v3/views/auth.py` wraps SimpleJWT views for `/auth/login`, `/auth/refresh`, and `/auth/blacklist` under the `api_v3` namespace while leaving legacy `/api/token/*` intact.
- Serializers/Filters: reuse `SampleV3Serializer`, `SampleV3DetailSerializer`, and `SampleV3Filter` (move or import). Pagination uses `SamplePageNumberPagination` or a dedicated class in `api_v3` if decoupling is needed.
- Auth: expose SimpleJWT-powered login/refresh/blacklist inside `api_v3` for the frontend, while continuing to serve the legacy endpoints in `users/urls.py` for templates; API views require `IsAuthenticated` unless explicitly set to `AllowAny`.
- Settings: maintain CORS origins for localhost:3000 and production domains; ensure `REST_FRAMEWORK` defaults, JWT settings, and `SPECTACULAR_SETTINGS` include the new namespace.

---
Plan updated on 2025-12-18 to incorporate the requirement that all frontend auth/profile endpoints live inside `api_v3`, duplicating shared endpoints as needed while leaving legacy routes intact. Updated again on 2025-12-18 after scaffolding `api_v3`, rerouting v3 URLs, and adding duplicated auth/profile endpoints plus compatibility re-exports.
