<!--
Relative path: codex/plan_api_v3_users.md
Description: Migration plan to recreate users/views.py functionality as API-first endpoints under api_v3 for the Next.js frontend.
Why: Provides a reference roadmap before moving user/account features from server-rendered Django views to the new API backend.
-->
## Goal
Replicate the user/account behaviors currently implemented in `users/views.py` as JSON APIs inside `api_v3` so the Next.js frontend can own the UI while keeping parity with existing flows.

## Current behavior to match
- Email/password login view that authenticates users and establishes a session.
- Password reset: request reset email and confirm/reset with uid/token/new password.
- Token management: create/delete/refresh DRF token for the authenticated user (used for data exports).
- Staff-only user management: create user with random password + welcome email, edit user, toggle staff status, activate/deactivate account with guardrails (no self-demotion, no superuser edits).
- Profile self-edit: update own name/email fields.
- Password change for logged-in user with session preservation.
- Account dashboard: last 20 samples modified by the user.
- Management page helper: semicolon-separated list of all user emails.

## Assumptions / constraints
- Keep using SimpleJWT for frontend auth; `api_v3/views/auth.py` already exposes obtain/refresh/blacklist views, so new user endpoints should accept JWTs and return JSON (no template renders).
- Reuse existing utilities (`generate_random_password`, `send_welcome_email`) and forms/validators where sensible, but expose serializer-driven APIs.
- Preserve existing permissions/guards (staff-only actions, no superuser edits, block self-deactivate/self-remove staff).
- No database schema changes or migrations.

## Plan for api_v3 parity
1) **Auth endpoints**: rely on existing `/auth/login` (JWT obtain) and `/auth/refresh`/`/auth/blacklist` from `api_v3/views/auth.py`; add password reset request/confirm endpoints mirroring `password_reset_api` and `password_reset_confirm_api` behaviors with serializer validation and email context (`FRONTEND_BASE_URL` support).
2) **Password change**: add authenticated endpoint to change password (mirroring `PasswordChangeView`) that updates session hash and returns success/errors.
3) **Profile APIs**: add `GET/PATCH /users/me` to fetch/update current user fields allowed in `NewUserForm` (first/last name, email) with validation.
4) **Staff user management**: add staff-protected endpoints for listing non-superusers, creating users (random password + welcome email), updating users, and toggling staff/active flags with the same guardrails as the views.
5) **Token management**: expose authenticated endpoints to create/delete/refresh DRF auth tokens used for exports; respond with token string where applicable.
6) **User activity data**: add endpoint returning the last 20 samples modified by the current user (matches `account` view) using existing sample serializers; add staff endpoint returning all user emails (semicolon-joined or list) used by management page.
7) **Routing & docs**: register routes under `api_v3/urls.py` with clear namespacing (likely `/users/...` and `/management/...`) and annotate with `extend_schema` tags for Spectacular.
8) **Tests**: add API tests covering each new endpoint (permissions, validation, email triggers, guardrails for self/superuser protections) and sample-query outputs.
