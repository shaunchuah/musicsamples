<!--
1. Relative file location: codex/plans/fix-nav-user-component.md
2. Description: ExecPlan for delivering backend-backed identity data and logout wiring to the dashboard nav-user component.
3. Why: Captures a step-by-step design so contributors can implement the nav-user fix without prior repo knowledge.
-->

# Fix nav-user component to surface backend-driven identity and logout

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this file in accordance with `codex/PLANS.md`.

## Purpose / Big Picture

After this work, an authenticated dashboard user will see their name, email, and access level reflected accurately in the sidebar footer, and the “Log out” control in that menu will sign them out reliably. The data will come from the Django backend instead of only decoding the JWT, so future changes to access control propagate immediately. A tester will be able to click the profile menu, confirm the access badge, and trigger logout without manually clearing cookies.

## Progress

- [x] (2025-11-04 16:12Z) Audited existing `frontend/components/dashboard/nav-user.tsx` and backend `users/urls.py` to assess current data sources and gaps.
- [x] (2025-11-04 16:14Z) Drafted this ExecPlan skeleton with required sections per `codex/PLANS.md`.
- [x] (2025-11-04 16:19Z) Implemented DRF `CurrentUserAPIView`/serializer and registered `/users/api/me/`.
- [x] (2025-11-04 16:22Z) Added the `/api/dashboard/user` Next.js proxy that relays the backend profile.
- [x] (2025-11-04 16:26Z) Refreshed `NavUser` to hydrate from the proxy and wire logout handling.
- [x] (2025-11-04 16:30Z) Added pytest coverage plus `pnpm lint` verification for the new flow.

## Surprises & Discoveries

- None encountered during implementation.

## Decision Log

- Decision: Serve the user profile data via Django REST Framework using an authenticated API view at `/users/api/me/`.
  Rationale: The frontend is moving toward a DRF-backed backend; adopting DRF now keeps behaviour consistent, unlocks serializers for shaping the payload, and aligns with broader scaffolding goals.
  Date/Author: 2025-11-04 / Codex
- Decision: Derive a string `access_level` on the frontend from the returned `is_superuser` and `is_staff` flags (mapping to `"superuser"`, `"staff"`, or `"user"`), while keeping the raw booleans available for other logic.
  Rationale: Provides both a human-readable badge label and raw data for future conditional UI without requiring the backend to dictate presentation concerns.
  Date/Author: 2025-11-04 / Codex
- Decision: Include the user’s Django group memberships in the API response as a list of names.
  Rationale: Groups communicate access tiers used throughout the legacy admin; exposing them now supports future UI controls without another backend change.
  Date/Author: 2025-11-04 / Codex
- Decision: Implement a Next.js API route at `/api/dashboard/user` that proxies to the Django endpoint and returns a cached JSON response to client components.
  Rationale: Keeps HTTP-only cookies on the server, mirroring the existing samples proxy pattern and avoiding token handling in the browser.
  Date/Author: 2025-11-04 / Codex

## Outcomes & Retrospective

- Implementation complete. The frontend now calls a DRF current-user endpoint via a proxy, displays access labels derived from staff/superuser/group flags, and exposes a working logout action in the sidebar dropdown. Tests confirm the API contract, lint passes, and no database changes were required. Follow-up: if future components need the same logout handler, extract it into a shared utility.

## Context and Orientation

The dashboard sidebar renders via `frontend/components/dashboard/app-sidebar.tsx`, which injects the `NavUser` component from `frontend/components/dashboard/nav-user.tsx`. `NavUser` is a client component that currently receives `firstName`, `lastName`, `email`, and an optional `avatar` URL and builds a dropdown menu using shared Shadcn UI primitives under `frontend/components/ui`. The logout menu item is present visually but has no click handler. The surrounding page (`frontend/app/page.tsx`) derives user details by parsing the JWT stored in the HTTP-only `authToken` cookie and passes that data into `AppSidebar`. On the backend, `users/urls.py` exposes forms-based views and password-reset JSON endpoints but lacks an authenticated JSON route to read the current user profile. Existing Next.js API routes under `frontend/app/api/dashboard/samples` demonstrate the approved proxy pattern for fetching backend data with bearer tokens. We must respect the project rule to activate the Python virtual environment (`source venv/bin/activate`) before running commands, and we must not introduce database migrations.

## Plan of Work

First, extend the Django app by adding a DRF serializer and view to `users/views.py` (or a new `users/api_views.py` if separation helps). Define a `CurrentUserSerializer` that exposes `email`, `first_name`, `last_name`, `is_staff`, `is_superuser`, and `groups`, where `groups` is a list of group names derived from `request.user.groups.values_list("name", flat=True)`. Implement an authenticated DRF `APIView` (for example `RetrieveAPIView`) named `CurrentUserAPIView` that enforces `IsAuthenticated`, serializes `request.user`, and returns the serializer data. Register this view in `users/urls.py` under `path("api/me/", CurrentUserAPIView.as_view(), name="current_user_api")`. Add DRF-based tests under `users/tests` that authenticate via the Django test client, request `/users/api/me/`, and assert the JSON includes the specified fields and group names for both staff and non-staff accounts. Update DRF authentication settings if the project requires adjustments so the view honours the JWT-based session already in use.

Next, mirror the existing samples proxy to keep tokens server-side. Create `frontend/app/api/dashboard/user/route.ts` that reads the `AUTH_COOKIE_NAME` access token from cookies, calls the backend `/users/api/me/` endpoint with an `Authorization: Bearer <token>` header, and returns the JSON to the client. Handle missing tokens with a 401 and unexpected backend failures with a 502-style response. Type the response payload and export it so client components can reuse the interface.

Finally, refactor `frontend/components/dashboard/nav-user.tsx` to load this data. Introduce a `useEffect` that fetches `/api/dashboard/user` once when mounted, merging the server-provided prop with the backend payload. Compute any display-specific access label client-side from `is_superuser`, `is_staff`, or membership in privileged groups rather than relying on a backend-derived `access_level` string. Ensure the dropdown’s logout item invokes an asynchronous `handleLogout` function that POSTs to `/api/auth/logout`, clears loading state, and redirects to `/login` using `useRouter`, following the existing implementation in `frontend/components/dashboard/user-profile-menu.tsx`. Update associated TypeScript types (e.g. extend `DashboardUser`) so `AppSidebar` passes the minimal initial identity while `NavUser` enriches it. Include graceful fallbacks if the fetch fails so the component still renders with JWT data.

## Concrete Steps

All commands run from the repository root after sourcing the virtualenv.

    source venv/bin/activate
    pytest users/tests/test_api_views.py
    cd frontend && pnpm lint

Add any additional targeted pytest invocations if you split tests into a new file, and document them here as the implementation evolves.

## Validation and Acceptance

A change is acceptable when an authenticated request to `/users/api/me/` returns the correct JSON fields (`email`, `first_name`, `last_name`, `is_staff`, `is_superuser`, `groups`) for different account roles, the Next.js proxy (`GET /api/dashboard/user`) relays that data while unauthenticated requests return 401, and the dashboard sidebar shows the expected name, email, and an access badge derived from the returned flags or groups with real user data. Trigger the logout menu item and confirm it clears the cookies and redirects to `/login`. Automated acceptance entails the new pytest coverage passing and the frontend lint/type-checks succeeding.

## Idempotence and Recovery

The new API route is read-only and safe to call repeatedly; the Next.js proxy simply forwards responses and can be re-run without side-effects. If a component fetch fails, the UI should continue rendering base JWT data. Recovery from coding errors involves reverting the touched files with `git checkout -- <path>` before committing; no database or migration state is altered.

## Artifacts and Notes

- pytest users/tests/test_api_views.py .. [100%]
- pnpm lint → Checked 62 files, no fixes applied.

## Interfaces and Dependencies

Backend: introduce a `CurrentUserSerializer` in `users` exposing the fields above and a `CurrentUserAPIView` that authenticates, serializes `request.user`, and returns DRF `Response` data shaped as

    {
      "email": string,
      "first_name": string | null,
      "last_name": string | null,
      "is_staff": boolean,
      "is_superuser": boolean,
      "groups": string[]
    }

Frontend proxy: define `frontend/app/api/dashboard/user/route.ts` exporting `GET(request: Request)`, which returns the same JSON shape or `{ "detail": "Unauthorized" }` with 401. Client type: extend `DashboardUser` in `frontend/components/dashboard/user-profile-menu.tsx` (and re-export from a shared file if reused) to include optional `isStaff?: boolean; isSuperuser?: boolean; groups?: string[]; accessLevel?: "superuser" | "staff" | "user"`.

## Change Log

- 2025-11-04: Initial ExecPlan drafted for the nav-user fix (Codex).
- 2025-11-04: Updated plan to adopt a DRF API view returning user profile fields and groups (Codex).
- 2025-11-04: Executed plan delivering DRF endpoint, proxy, nav-user integration, and tests (Codex).
- 2025-11-04: Removed unused `UserProfileMenu` component and moved `DashboardUser` typing into `frontend/types/dashboard.ts` (Codex).
