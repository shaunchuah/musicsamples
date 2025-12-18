// frontend/components/users/users-table.tsx
// Renders the staff user management UI with shadcn table + TanStack sorting and dialog forms.
// Exists to keep feature parity with the legacy Django user list while using api_v3 and the Next.js dashboard shell.

"use client";

import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { useCallback, useEffect, useMemo, useState } from "react";

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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { UserFormDialog } from "./user-form-dialog";
import { JOB_TITLE_OPTIONS, optionLabel, PRIMARY_ORG_OPTIONS } from "./user-options";
import type {
  DisplayUser,
  PendingAction,
  StaffUser,
  StatusMessage,
  UserAction,
  UserFormValues,
  UsersListResponse,
} from "./user-types";
import { buildUserColumns, userSortingFns } from "./users-table-columns";

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
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);
  const [sorting, setSorting] = useState<SortingState>([]);

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

  const columns = useMemo(
    () =>
      buildUserColumns({
        actionInFlight,
        startEdit,
        setPendingAction,
      }),
    [actionInFlight, startEdit, setPendingAction],
  );

  const table = useReactTable({
    data: displayRows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    sortingFns: userSortingFns,
  });

  const isEmpty = !displayRows.length && !isLoading && !error;

  return (
    <div className="space-y-4">
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
                    pendingAction?.action === "deactivate" ||
                    pendingAction?.action === "remove_staff"
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
