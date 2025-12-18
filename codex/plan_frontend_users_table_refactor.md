<!-- codex/plan_frontend_users_table_refactor.md -->
<!-- Planning for breaking the users table component into smaller pieces. -->
<!-- Exists to track the refactor steps requested for the users table file. -->

1) Extract shared types/constants to reusable modules so components stay slim.
2) Move the dialog and column definitions out of `users-table.tsx`.
3) Keep table logic in the main file and wire imports to new modules.
