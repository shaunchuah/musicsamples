// frontend/components/users/users-table.tsx
// Renders the staff user management UI with shadcn table + TanStack sorting and dialog forms.
// Exists to keep feature parity with the legacy Django user list while using api_v3 and the Next.js dashboard shell.

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type HeaderContext,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AlertDescription, AlertError, AlertSuccess } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type StaffUser = {
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

type UsersListResponse = {
  results?: StaffUser[];
  count?: number;
  detail?: string;
  error?: string;
};

type UserAction = "make_staff" | "remove_staff" | "activate" | "deactivate";

type UserFormValues = {
  email: string;
  first_name: string;
  last_name: string;
  job_title: string;
  primary_organisation: string;
};

type StatusMessage = {
  type: "success" | "error";
  text: string;
};

type ManagementEmails = {
  emails: string[];
  emails_joined: string;
};

const JOB_TITLE_OPTIONS = [
  { value: "", label: "Select job title" },
  { value: "research_assistant", label: "Research Assistant" },
  { value: "postdoctoral_researcher", label: "Postdoctoral Researcher" },
  { value: "phd_student", label: "PhD Student" },
  { value: "clinical_research_fellow", label: "Clinical Research Fellow" },
  { value: "clinical_research_nurse", label: "Clinical Research Nurse" },
  { value: "clinician_scientist", label: "Clinician Scientist" },
  { value: "scientist", label: "Scientist" },
  { value: "unknown", label: "Unknown" },
];

const PRIMARY_ORG_OPTIONS = [
  { value: "", label: "Select primary organisation" },
  { value: "nhs_lothian", label: "NHS Lothian" },
  { value: "nhs_ggc", label: "NHS GGC" },
  { value: "nhs_tayside", label: "NHS Tayside" },
  { value: "university_of_edinburgh", label: "University of Edinburgh" },
  { value: "university_of_glasgow", label: "University of Glasgow" },
  { value: "university_of_dundee", label: "University of Dundee" },
  { value: "unknown", label: "Unknown" },
];

type DisplayUser = StaffUser & {
  displayName: string;
  jobTitleLabel: string;
  primaryOrgLabel: string;
  groupsLabel: string;
};

const jobTitleEnum = z.enum(
  JOB_TITLE_OPTIONS.filter((option) => option.value).map((option) => option.value) as [
    string,
    ...string[],
  ],
);

const primaryOrgEnum = z.enum(
  PRIMARY_ORG_OPTIONS.filter((option) => option.value).map((option) => option.value) as [
    string,
    ...string[],
  ],
);

const dialogSchema = z.object({
  email: z.string().email("Enter a valid email."),
  first_name: z.string().min(1, "First name is required."),
  last_name: z.string().min(1, "Last name is required."),
  job_title: z.union([z.literal(""), jobTitleEnum]),
  primary_organisation: z.union([z.literal(""), primaryOrgEnum]),
});

const datetimeFormatter = new Intl.DateTimeFormat("en-GB", {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return datetimeFormatter.format(date);
}

function normalisePayload(values: UserFormValues): UserFormValues {
  return {
    ...values,
    job_title: values.job_title?.trim() ?? "",
    primary_organisation: values.primary_organisation?.trim() ?? "",
  };
}

function sortDate(a: unknown, b: unknown): number {
  const aValue = (a as string | null | undefined) ?? "";
  const bValue = (b as string | null | undefined) ?? "";
  const aTime = aValue ? new Date(aValue).getTime() : Number.NEGATIVE_INFINITY;
  const bTime = bValue ? new Date(bValue).getTime() : Number.NEGATIVE_INFINITY;
  if (Number.isNaN(aTime) && Number.isNaN(bTime)) return 0;
  if (Number.isNaN(aTime)) return -1;
  if (Number.isNaN(bTime)) return 1;
  return aTime === bTime ? 0 : aTime > bTime ? 1 : -1;
}

function optionLabel(
  options: { value: string; label: string }[],
  value: string | null | undefined,
): string {
  if (!value) return "—";
  const match = options.find((option) => option.value === value);
  return match?.label ?? value;
}

type UserFormDialogProps = {
  mode: "create" | "edit";
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultValues: StaffUser | null;
  onSubmit: (values: UserFormValues, userId?: number) => Promise<void>;
};

function UserFormDialog({
  mode,
  open,
  onOpenChange,
  defaultValues,
  onSubmit,
}: UserFormDialogProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<UserFormValues>({
    resolver: zodResolver(dialogSchema),
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      job_title: "",
      primary_organisation: "",
    },
  });

  useEffect(() => {
    form.reset({
      email: defaultValues?.email ?? "",
      first_name: defaultValues?.first_name ?? "",
      last_name: defaultValues?.last_name ?? "",
      job_title: defaultValues?.job_title ?? "",
      primary_organisation: defaultValues?.primary_organisation ?? "",
    });
    setSubmitError(null);
  }, [defaultValues, form, open]);

  const handleSubmit = useCallback(
    async (values: UserFormValues) => {
      setSubmitError(null);
      try {
        await onSubmit(normalisePayload(values), defaultValues?.id);
        onOpenChange(false);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unable to save user.";
        setSubmitError(message);
      }
    },
    [defaultValues?.id, onOpenChange, onSubmit],
  );

  const isSubmitting = form.formState.isSubmitting;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{mode === "create" ? "Add New User" : "Edit User"}</DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "Create a new account for a team member. A welcome email will be sent automatically."
              : "Update the user details shown in the management table."}
          </DialogDescription>
        </DialogHeader>

        {submitError ? (
          <AlertError>
            <AlertDescription>{submitError}</AlertDescription>
          </AlertError>
        ) : null}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      autoComplete="email"
                      placeholder="user@example.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>First name</FormLabel>
                    <FormControl>
                      <Input autoComplete="given-name" placeholder="First name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Last name</FormLabel>
                    <FormControl>
                      <Input autoComplete="family-name" placeholder="Last name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="job_title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Job title</FormLabel>
                  <FormControl>
                    <select
                      name={field.name}
                      value={field.value ?? ""}
                      onChange={(event) => field.onChange(event.target.value)}
                      onBlur={field.onBlur}
                      ref={field.ref}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      {JOB_TITLE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="primary_organisation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Primary organisation</FormLabel>
                  <FormControl>
                    <select
                      name={field.name}
                      value={field.value ?? ""}
                      onChange={(event) => field.onChange(event.target.value)}
                      onBlur={field.onBlur}
                      ref={field.ref}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      {PRIMARY_ORG_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : mode === "create" ? "Create user" : "Save changes"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

export function UsersTable() {
  const [users, setUsers] = useState<StaffUser[]>([]);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<StatusMessage | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<"create" | "edit">("create");
  const [selectedUser, setSelectedUser] = useState<StaffUser | null>(null);
  const [actionInFlight, setActionInFlight] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<{ user: DisplayUser; action: UserAction } | null>(null);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [emails, setEmails] = useState<ManagementEmails | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);

  const loadUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/dashboard/users", { cache: "no-store" });
      const payload = (await response.json().catch(() => null)) as
        | UsersListResponse
        | StaffUser[]
        | null;

      if (!response.ok) {
        const detail =
          (payload as UsersListResponse | null)?.detail ??
          (payload as UsersListResponse | null)?.error;
        throw new Error(detail ?? "Unable to fetch users.");
      }

      const rows = Array.isArray(payload) ? payload : (payload?.results ?? []);
      setUsers(rows);
      setTotalCount(
        typeof (payload as UsersListResponse | null)?.count === "number"
          ? ((payload as UsersListResponse).count ?? null)
          : rows.length,
      );
    } catch (fetchError) {
      const message = fetchError instanceof Error ? fetchError.message : "Unable to fetch users.";
      setError(message);
      setUsers([]);
      setTotalCount(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const loadEmails = useCallback(async () => {
    setEmailError(null);
    try {
      const response = await fetch("/api/dashboard/users?variant=emails", { cache: "no-store" });
      const payload = (await response.json().catch(() => null)) as
        | ManagementEmails
        | { detail?: string }
        | null;

      if (!response.ok) {
        throw new Error(
          (payload as { detail?: string } | null)?.detail ?? "Unable to fetch emails.",
        );
      }

      setEmails(payload as ManagementEmails);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to fetch emails.";
      setEmailError(message);
      setEmails(null);
    }
  }, []);

  useEffect(() => {
    void loadEmails();
  }, [loadEmails]);

  const handleDialogSubmit = useCallback(
    async (values: UserFormValues, userId?: number) => {
      const endpoint = userId ? `/api/dashboard/users/${userId}` : "/api/dashboard/users";
      const method = userId ? "PATCH" : "POST";

      const response = await fetch(endpoint, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      });

      const payload = (await response.json().catch(() => null)) as UsersListResponse | null;

      if (!response.ok) {
        throw new Error(payload?.detail ?? payload?.error ?? "Unable to save user.");
      }

      await loadUsers();
      setStatusMessage({
        type: "success",
        text: userId ? "User updated successfully." : "User created successfully.",
      });
    },
    [loadUsers],
  );

  const handleAction = useCallback(
    async (userId: number, action: UserAction) => {
      const actionKey = `${action}-${userId}`;
      setActionInFlight(actionKey);
      setStatusMessage(null);

      try {
        const response = await fetch(`/api/dashboard/users/${userId}/${action}`, {
          method: "POST",
        });

        const payload = (await response.json().catch(() => null)) as UsersListResponse | null;

        if (!response.ok) {
          throw new Error(payload?.detail ?? payload?.error ?? "Unable to update user.");
        }

        await loadUsers();
        setStatusMessage({ type: "success", text: "User settings updated." });
      } catch (actionError) {
        const message =
          actionError instanceof Error ? actionError.message : "Unable to update user.";
        setStatusMessage({ type: "error", text: message });
      } finally {
        setActionInFlight(null);
      }
    },
    [loadUsers],
  );

  const startCreate = useCallback(() => {
    setDialogMode("create");
    setSelectedUser(null);
    setDialogOpen(true);
  }, []);

  const startEdit = useCallback((user: StaffUser) => {
    setDialogMode("edit");
    setSelectedUser(user);
    setDialogOpen(true);
  }, []);

  const displayRows: DisplayUser[] = useMemo(
    () =>
      users.map((user) => ({
        ...user,
        displayName:
          [user.first_name, user.last_name].filter(Boolean).join(" ").trim() || user.email,
        jobTitleLabel: optionLabel(JOB_TITLE_OPTIONS, user.job_title),
        primaryOrgLabel: optionLabel(PRIMARY_ORG_OPTIONS, user.primary_organisation),
        groupsLabel: user.groups?.length ? user.groups.join(", ") : "—",
      })),
    [users],
  );

  const columns: ColumnDef<DisplayUser>[] = useMemo(
    () => [
      {
        accessorKey: "displayName",
        id: "displayName",
        header: ({ column }) => <HeaderButton label="Name" column={column} />,
        cell: ({ row }) => (
          <span className="font-medium text-foreground">{row.original.displayName}</span>
        ),
        sortingFn: "alphanumeric",
      },
      {
        accessorKey: "email",
        header: ({ column }) => <HeaderButton label="Email" column={column} />,
        cell: ({ row }) => <span className="text-muted-foreground">{row.original.email}</span>,
        sortingFn: "alphanumeric",
      },
      {
        accessorKey: "jobTitleLabel",
        header: ({ column }) => <HeaderButton label="Job Title" column={column} />,
        cell: ({ row }) => (
          <span className="text-muted-foreground">{row.original.jobTitleLabel}</span>
        ),
        sortingFn: "alphanumeric",
      },
      {
        accessorKey: "primaryOrgLabel",
        header: ({ column }) => <HeaderButton label="Primary Org" column={column} />,
        cell: ({ row }) => (
          <span className="text-muted-foreground">{row.original.primaryOrgLabel}</span>
        ),
        sortingFn: "alphanumeric",
      },
      {
        accessorKey: "groupsLabel",
        header: ({ column }) => <HeaderButton label="Groups" column={column} />,
        cell: ({ row }) => (
          <span className="text-muted-foreground">{row.original.groupsLabel}</span>
        ),
        sortingFn: "alphanumeric",
      },
      {
        accessorKey: "is_staff",
        header: ({ column }) => <HeaderButton label="Staff" column={column} />,
        cell: ({ row }) => (
          <span
            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
              row.original.is_staff
                ? "bg-emerald-50 text-emerald-700"
                : "bg-amber-50 text-amber-700"
            }`}
          >
            {row.original.is_staff ? "Staff" : "Standard"}
          </span>
        ),
        sortingFn: "basic",
      },
      {
        accessorKey: "is_active",
        header: ({ column }) => <HeaderButton label="Active" column={column} />,
        cell: ({ row }) => (
          <span
            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
              row.original.is_active ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
            }`}
          >
            {row.original.is_active ? "Active" : "Inactive"}
          </span>
        ),
        sortingFn: "basic",
      },
      {
        accessorKey: "last_login",
        header: ({ column }) => <HeaderButton label="Last Login" column={column} />,
        cell: ({ row }) => (
          <span className="text-muted-foreground">{formatDate(row.original.last_login)}</span>
        ),
        sortingFn: "datetime",
      },
      {
        accessorKey: "date_joined",
        header: ({ column }) => <HeaderButton label="Date Joined" column={column} />,
        cell: ({ row }) => (
          <span className="text-muted-foreground">{formatDate(row.original.date_joined)}</span>
        ),
        sortingFn: "datetime",
      },
      {
        id: "edit",
        header: () => <span className="font-medium">Edit</span>,
        enableSorting: false,
        cell: ({ row }) => (
          <Button
            variant="outline"
            size="sm"
            onClick={() => startEdit(row.original)}
            disabled={Boolean(actionInFlight)}
          >
            Edit
          </Button>
        ),
      },
      {
        id: "staff_actions",
        header: () => <span className="font-medium">Staff</span>,
        enableSorting: false,
        cell: ({ row }) => {
          const user = row.original;
          const staffAction: UserAction = user.is_staff ? "remove_staff" : "make_staff";
          const staffLabel = user.is_staff ? "Remove Staff" : "Make Staff";
          const staffBusy = actionInFlight === `${staffAction}-${user.id}`;

          return (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPendingAction({ user, action: staffAction })}
              disabled={staffBusy || Boolean(actionInFlight)}
            >
              {staffBusy ? "Working..." : staffLabel}
            </Button>
          );
        },
      },
      {
        id: "active_actions",
        header: () => <span className="font-medium">Active</span>,
        enableSorting: false,
        cell: ({ row }) => {
          const user = row.original;
          const activeAction: UserAction = user.is_active ? "deactivate" : "activate";
          const activeLabel = user.is_active ? "Deactivate" : "Activate";
          const activeBusy = actionInFlight === `${activeAction}-${user.id}`;

          return (
            <Button
              variant={user.is_active ? "destructive" : "default"}
              size="sm"
              onClick={() => setPendingAction({ user, action: activeAction })}
              disabled={activeBusy || Boolean(actionInFlight)}
            >
              {activeBusy ? "Working..." : activeLabel}
            </Button>
          );
        },
      },
    ],
    [actionInFlight, startEdit],
  );

  const table = useReactTable({
    data: displayRows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    sortingFns: {
      datetime: (rowA, rowB, columnId) =>
        sortDate(rowA.getValue(columnId), rowB.getValue(columnId)),
      basic: (rowA, rowB, columnId) => {
        const a = rowA.getValue(columnId) as string | number | boolean | null | undefined;
        const b = rowB.getValue(columnId) as string | number | boolean | null | undefined;
        if (a === b) return 0;
        if (a === null || a === undefined) return -1;
        if (b === null || b === undefined) return 1;
        return a > b ? 1 : -1;
      },
    },
  });

  const isEmpty = !displayRows.length && !isLoading && !error;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>User email list</CardTitle>
          <CardDescription>Copy all user emails for bulk messages.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {emailError ? (
            <AlertError>
              <AlertDescription>{emailError}</AlertDescription>
            </AlertError>
          ) : null}
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
            <Input
              readOnly
              value={emails?.emails_joined ?? "Loading emails..."}
              className="flex-1"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                if (!emails?.emails_joined) return;
                void navigator.clipboard.writeText(emails.emails_joined).then(
                  () => setCopyStatus("Copied"),
                  () => setCopyStatus("Unable to copy"),
                );
              }}
              disabled={!emails?.emails_joined}
            >
              {copyStatus ?? "Copy"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="gap-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle>User Management</CardTitle>
              <CardDescription>
                Staff-only controls for creating, editing, and toggling users.
              </CardDescription>
            </div>
            <div className="flex flex-col items-start gap-2 sm:flex-row sm:items-center sm:gap-3">
              <div className="text-sm text-muted-foreground">Total Count: {totalCount ?? "—"}</div>
              <Button onClick={startCreate}>Add New User</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {statusMessage ? (
            statusMessage.type === "success" ? (
              <AlertSuccess>
                <AlertDescription>{statusMessage.text}</AlertDescription>
              </AlertSuccess>
            ) : (
              <AlertError>
                <AlertDescription>{statusMessage.text}</AlertDescription>
              </AlertError>
            )
          ) : null}

          {error ? (
            <AlertError>
              <AlertDescription>{error}</AlertDescription>
            </AlertError>
          ) : null}

          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={columns.length} className="text-muted-foreground">
                    Loading users...
                  </TableCell>
                </TableRow>
              ) : isEmpty ? (
                <TableRow>
                  <TableCell colSpan={columns.length} className="text-muted-foreground">
                    No users found.
                  </TableCell>
                </TableRow>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <UserFormDialog
            mode={dialogMode}
            open={dialogOpen}
            onOpenChange={setDialogOpen}
            defaultValues={selectedUser}
            onSubmit={handleDialogSubmit}
          />

          <Dialog
            open={Boolean(pendingAction)}
            onOpenChange={(open) => {
              if (!open) setPendingAction(null);
            }}
          >
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {pendingAction
                    ? pendingAction.action === "deactivate"
                      ? `Deactivate ${pendingAction.user.displayName}'s account?`
                      : pendingAction.action === "activate"
                        ? `Activate ${pendingAction.user.displayName}'s account?`
                        : pendingAction.action === "make_staff"
                          ? `Make ${pendingAction.user.displayName} a staff member?`
                          : `Remove staff access for ${pendingAction.user.displayName}?`
                    : ""}
                </DialogTitle>
                <DialogDescription>
                  {pendingAction
                    ? pendingAction.action === "deactivate"
                      ? "They will no longer be able to sign in until reactivated."
                      : pendingAction.action === "activate"
                        ? "Restore their ability to access the dashboard."
                        : pendingAction.action === "make_staff"
                          ? "Grant staff permissions to manage users and data."
                          : "Revoke staff permissions from this account."
                    : ""}
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setPendingAction(null)}
                  disabled={Boolean(actionInFlight)}
                >
                  Cancel
                </Button>
                <Button
                  variant={
                    pendingAction?.action === "deactivate" || pendingAction?.action === "remove_staff"
                      ? "destructive"
                      : "default"
                  }
                  onClick={() => {
                    if (!pendingAction) return;
                    void handleAction(pendingAction.user.id, pendingAction.action);
                    setPendingAction(null);
                  }}
                  disabled={Boolean(actionInFlight)}
                >
                  {actionInFlight ? "Working..." : "Confirm"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </div>
  );
}

type HeaderButtonProps = {
  label: string;
  column: HeaderContext<DisplayUser, unknown>["column"];
};

function HeaderButton({ label, column }: HeaderButtonProps) {
  const state = column.getIsSorted();

  return (
    <button
      type="button"
      className="flex items-center gap-2 font-medium cursor-pointer"
      onClick={() => column.toggleSorting()}
    >
      {label}
      {state === "asc" ? (
        <ArrowUp className="h-4 w-4 text-foreground" aria-hidden />
      ) : state === "desc" ? (
        <ArrowDown className="h-4 w-4 text-foreground" aria-hidden />
      ) : (
        <ArrowUpDown className="h-4 w-4 text-muted-foreground" aria-hidden />
      )}
    </button>
  );
}
