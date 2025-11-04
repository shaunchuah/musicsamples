// frontend/types/dashboard.ts
// Defines shared type aliases for dashboard data consumed across pages.
// Exists so components can import consistent DashboardUser typing once `UserProfileMenu` is removed.

export type DashboardUser = {
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
  isStaff?: boolean;
  isSuperuser?: boolean;
  groups?: string[] | null;
  accessLevel?: "superuser" | "staff" | "user";
};
