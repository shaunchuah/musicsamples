// frontend/components/users/users-table-columns.tsx
// Builds the column definitions for the user management table with sorting controls.
// Exists to separate presentational table concerns from the data-fetching logic.

import type { ColumnDef, HeaderContext, SortingFn } from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ArrowUpDown, CheckIcon } from "lucide-react";

import { Button } from "@/components/ui/button";

import type { DisplayUser, PendingAction, StaffUser, UserAction } from "./user-types";

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

export const userSortingFns: Record<string, SortingFn<DisplayUser>> = {
  datetime: (rowA, rowB, columnId) => sortDate(rowA.getValue(columnId), rowB.getValue(columnId)),
  basic: (rowA, rowB, columnId) => {
    const a = rowA.getValue(columnId) as string | number | boolean | null | undefined;
    const b = rowB.getValue(columnId) as string | number | boolean | null | undefined;
    if (a === b) return 0;
    if (a === null || a === undefined) return -1;
    if (b === null || b === undefined) return 1;
    return a > b ? 1 : -1;
  },
};

type BuildUserColumnsParams = {
  actionInFlight: string | null;
  startEdit: (user: StaffUser) => void;
  setPendingAction: (value: PendingAction | null) => void;
};

export function buildUserColumns({
  actionInFlight,
  startEdit,
  setPendingAction,
}: BuildUserColumnsParams): ColumnDef<DisplayUser>[] {
  return [
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
      cell: ({ row }) => <span className="text-muted-foreground">{row.original.groupsLabel}</span>,
      sortingFn: "alphanumeric",
    },
    {
      accessorKey: "is_staff",
      header: ({ column }) => <HeaderButton label="Staff" column={column} />,
      cell: ({ row }) => (
        <span
          className={`inline-flex items-center rounded-full p-1 text-xs font-medium ${
            row.original.is_staff ? "bg-emerald-50 text-emerald-700" : null
          }`}
        >
          {row.original.is_staff ? <CheckIcon size="12" /> : ""}
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
        <span className="text-muted-foreground whitespace-nowrap">
          {formatDate(row.original.last_login)}
        </span>
      ),
      sortingFn: "datetime",
    },
    {
      accessorKey: "date_joined",
      header: ({ column }) => <HeaderButton label="Date Joined" column={column} />,
      cell: ({ row }) => (
        <span className="text-muted-foreground whitespace-nowrap">
          {formatDate(row.original.date_joined)}
        </span>
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
  ];
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
