// frontend/components/users/user-types.ts
// Shares the user management types between the table, dialog, and helper modules.
// Exists to avoid duplicating shapes as the user table is split into smaller files.

export type StaffUser = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  job_title: string | null;
  primary_organisation: string | null;
  is_staff: boolean;
  is_active: boolean;
  last_login?: string | null;
  date_joined?: string | null;
  groups?: string[];
};

export type UsersListResponse = {
  results?: StaffUser[];
  count?: number;
  detail?: string;
  error?: string;
};

export type UserAction = "make_staff" | "remove_staff" | "activate" | "deactivate";

export type UserFormValues = {
  email: string;
  first_name: string;
  last_name: string;
  job_title: string;
  primary_organisation: string;
  groups: string[];
};

export type StatusMessage = {
  type: "success" | "error";
  text: string;
};

export type ManagementEmails = {
  emails: string[];
  emails_joined: string;
};

export type DisplayUser = StaffUser & {
  displayName: string;
  jobTitleLabel: string;
  primaryOrgLabel: string;
  groupsLabel: string;
};

export type PendingAction = { user: DisplayUser; action: UserAction };
