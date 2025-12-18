<!--
Relative path: codex/plan_user_group_editing.md
Description: Plan to enable editing of Django auth groups in the user management dashboard.
Why: Document the approach for adding group assignment controls to the user form while keeping backend and frontend in sync.
-->
## Current state
- Staff users returned from `/api/v3/users/` include `groups` (names) but the create/edit flow ignores them; the dialog only handles email/name/job title/primary org.
- No backend endpoint exposes the available groups list, and the `StaffUserUpdateSerializer` does not accept group assignments.
- The Next.js proxy and form types mirror the limited fields, so group choices cannot be loaded or sent.

## Plan
1) Extend backend support for groups: update the staff user serializer used for create/update to accept a list of group names, map them to `Group` relations safely (ignore/validate unknown names), and keep `StaffUserSerializer` returning names.
2) Expose available groups: add a staff-protected endpoint returning group names (@action on `StaffUserViewSet`) and proxy it via `/api/users/groups` for the frontend to consume.
3) Broaden frontend types/validation: include `groups: string[]` in `UserFormValues` and schema defaults so create/edit flows can capture selections.
4) UI wiring: fetch group options when preparing the dialog (or alongside users), pass them into `UserFormDialog`, and render checkboxes with existing memberships pre-checked for edits.
5) Submission flow: send `groups` in POST/PATCH payloads through the dashboard API proxy, refresh the table, and keep `groupsLabel` derived from returned data.
6) Tests/error handling: cover group option fetch failures and successful submissions that include groups in unit tests (frontend) and add backend serializer/action tests around group assignment validation.
