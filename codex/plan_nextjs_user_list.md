<!--
Relative path: codex/plan_nextjs_user_list.md
Description: Plan to port the legacy Django user list page to the Next.js frontend using the api_v3 backend routes.
Why: Document the steps required to recreate staff user management in the new app while keeping parity with current behavior.
-->
## What the legacy page does
- Staff-only table of non-superusers ordered by active status and last login, with total count and an "Add New User" CTA.
- Columns: name, email, edit profile link, staff badge with toggle actions, last login, date joined, active badge, activate/deactivate actions.
- Guardrails: superusers excluded; self-deactivate and self-remove-staff blocked; messages shown on errors/success in Django.

## api_v3 surface to consume
- `GET /api/v3/users/`: list non-superusers ordered by `-is_active,-last_login`; staff-only; fields include id/email/first_name/last_name/job_title/primary_organisation/is_staff/is_active.
- `POST /api/v3/users/`: create user (random password + welcome email sent automatically); validation error on duplicate email.
- `PATCH /api/v3/users/{id}/`: edit user fields (cannot edit superusers; same serializer as create).
- Actions: `POST /api/v3/users/{id}/make_staff`, `/remove_staff`, `/activate`, `/deactivate` (block self-demotion/deactivate and superuser edits; return success/error JSON).

## Plan for the Next.js user list
1) Add a staff-protected route at `frontend/app/users` that server-fetches `/api/v3/users/` with the staff JWT and renders initial data or redirects on 401/403.
2) Build a minimal table matching legacy columns (name/email/edit/staff status/actions/last login/date joined/active/actions) plus total count and an "Add New User" button that opens a shadcn dialog.
3) Implement create/edit via a shared user form rendered inside a shadcn dialog: POST for create, PATCH for update; show inline validation (duplicate email, required fields) and success toasts; close dialog and refresh list on success.
4) Wire row actions: `Make/Remove Staff` and `Activate/Deactivate` call their POST actions with auth headers, surface API guardrail errors inline/toast, and refresh the table data.
5) Add loading/error states and minimal optimistic UX; if API pagination is enabled later, support limit/offset params while preserving ordering by active/last_login to match legacy.
6) Write frontend tests (React Testing Library/MSW) covering render, dialog form flows (create/edit), action calls, and error handling for 403/self-action guardrails; ensure auth headers are included and UI responds to backend messages.
