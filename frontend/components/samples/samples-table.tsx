// frontend/components/samples/samples-table.tsx
// Renders the landing-page samples table using TanStack Table and live backend data.
// Gives authenticated users a quick overview of recent samples pulled from the Django API.

"use client";

import {
  type Column,
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  type PaginationState,
  type SortingState,
  useReactTable,
  type VisibilityState,
} from "@tanstack/react-table";
import {
  Archive,
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Download,
  Edit,
  Eye,
  Settings,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { buildBackendUrl } from "@/lib/auth";

type StudyIdentifierSummary = {
  id: number;
  name: string;
};

type SampleRow = {
  id: number;
  sample_id: string;
  study_name: string;
  study_name_label: string | null;
  study_identifier: StudyIdentifierSummary | null;
  sample_location: string;
  sample_sublocation: string | null;
  sample_type: string;
  sample_type_label: string | null;
  sample_datetime: string | null;
  timepoint_label: string | null;
  study_group_label: string | null;
  age: number | null;
  sex_label: string | null;
  study_center_label: string | null;
  crp: number | null;
  calprotectin: number | null;
  endoscopic_mucosal_healing_at_3_6_months: boolean | null;
  endoscopic_mucosal_healing_at_12_months: boolean | null;
  genotype_data_available: boolean | null;
  sample_comments: string | null;
  is_used: boolean;
};

type SampleApiPayload = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: SampleRow[];
};

const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

const timeFormatter = new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
});

const EMPTY_STATE: SampleRow[] = [];
const DEFAULT_PAGE_SIZE = 50;

const SORT_FIELD_MAP: Record<string, string> = {
  study_name: "study_name",
  sample_id: "sample_id",
  study_identifier: "study_id__name",
  sample_location: "sample_location",
  sample_sublocation: "sample_sublocation",
  sample_type: "sample_type",
  sample_datetime: "sample_datetime",
};

type PaginationControlsProps = {
  canPrevious: boolean;
  canNext: boolean;
  isLoading: boolean;
  onPrevious: () => void;
  onNext: () => void;
  pageIndex: number;
  pageCount: number;
  firstItemIndex: number;
  lastItemIndex: number;
  totalLabel: number | string;
};

function PaginationControls({
  canPrevious,
  canNext,
  isLoading,
  onPrevious,
  onNext,
  pageIndex,
  pageCount,
  firstItemIndex,
  lastItemIndex,
  totalLabel,
}: PaginationControlsProps) {
  return (
    <div className="flex flex-col gap-2 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
      <p>
        Showing {firstItemIndex === 0 ? 0 : firstItemIndex}-{lastItemIndex} of {totalLabel} samples
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onPrevious}
          disabled={!canPrevious || isLoading}
        >
          Previous
        </Button>
        <span>
          Page {pageCount === 0 ? 0 : pageIndex + 1}
          {pageCount > 0 ? ` of ${pageCount}` : ""}
        </span>
        <Button variant="outline" size="sm" onClick={onNext} disabled={!canNext || isLoading}>
          Next
        </Button>
      </div>
    </div>
  );
}

function SortIndicator({ column }: { column: Column<SampleRow, unknown> }) {
  const state = column.getIsSorted();
  if (!state) {
    return <ArrowUpDown className="h-3 w-3 text-muted-foreground" />;
  }
  if (state === "asc") {
    return <ArrowUp className="h-3 w-3 text-muted-foreground" />;
  }
  return <ArrowDown className="h-3 w-3 text-muted-foreground" />;
}

function SortableHeader({ column, title }: { column: Column<SampleRow, unknown>; title: string }) {
  return (
    <button
      type="button"
      className="flex items-center gap-1 focus-visible:outline-none focus-visible:ring-0"
      onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
    >
      <span>{title}</span>
      <SortIndicator column={column} />
    </button>
  );
}

function formatMaybe(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "string" && value.trim() === "") {
    return "";
  }
  return String(value);
}

function formatBoolean(value: boolean | null | undefined): string {
  if (value === null || value === undefined) {
    return "";
  }
  return value ? "Yes" : "";
}

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "";
  }
  return `${value}`;
}

function formatDate(value: string | null): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const datePart = dateFormatter.format(date);
  const timePart = timeFormatter.format(date);
  return `${datePart} ${timePart}`; // No comma, just a space
}

export function SamplesTable() {
  const [rows, setRows] = useState<SampleRow[]>(EMPTY_STATE);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: DEFAULT_PAGE_SIZE,
  });
  const [pageCount, setPageCount] = useState(1);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({
    timepoint_label: false,
    study_group_label: false,
    age: false,
    sex_label: false,
    study_center_label: false,
    crp: false,
    calprotectin: false,
    endoscopic_mucosal_healing_at_3_6_months: false,
    endoscopic_mucosal_healing_at_12_months: false,
    genotype_data_available: false,
  });
  const [sorting, setSorting] = useState<SortingState>([]);

  useEffect(() => {
    setPagination((previous) => {
      if (previous.pageIndex === 0) {
        return previous;
      }
      return { ...previous, pageIndex: 0 };
    });
  }, [sorting]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadSamples() {
      setIsLoading(true);
      setError(null);
      setRows(EMPTY_STATE);

      try {
        const { pageIndex, pageSize } = pagination;
        const query = new URLSearchParams({
          page: String(pageIndex + 1),
          page_size: String(pageSize),
        });

        const orderingValues = sorting
          .map(({ id, desc }) => {
            const field = SORT_FIELD_MAP[id];
            if (!field) {
              return null;
            }
            return `${desc ? "-" : ""}${field}`;
          })
          .filter((value): value is string => Boolean(value));

        if (orderingValues.length > 0) {
          query.set("ordering", orderingValues.join(","));
        }

        const response = await fetch(`/api/dashboard/samples?${query.toString()}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch samples (${response.status})`);
        }

        const payload = (await response.json()) as SampleApiPayload | SampleRow[];

        const items: SampleRow[] = Array.isArray(payload)
          ? payload
          : Array.isArray(payload?.results)
            ? payload.results
            : EMPTY_STATE;

        setRows(items);

        const resolvedCount =
          typeof (payload as SampleApiPayload | undefined)?.count === "number"
            ? ((payload as SampleApiPayload).count ?? 0)
            : items.length;

        setTotalCount(resolvedCount);
        const totalPages = resolvedCount > 0 ? Math.ceil(resolvedCount / pagination.pageSize) : 1;
        setPageCount(totalPages);
      } catch (fetchError) {
        if (controller.signal.aborted) {
          return;
        }

        setError(fetchError instanceof Error ? fetchError.message : "Unknown error");
        setRows(EMPTY_STATE);
        setTotalCount(null);
        setPageCount(1);
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadSamples();

    return () => {
      controller.abort();
    };
  }, [pagination, sorting]);

  const columns = useMemo<ColumnDef<SampleRow>[]>(() => {
    return [
      {
        header: ({ column }) => <SortableHeader column={column} title="Study" />,
        accessorKey: "study_name",
        enableSorting: true,
        cell: ({ row }) => formatMaybe(row.original.study_name_label ?? row.original.study_name),
      },
      {
        header: ({ column }) => <SortableHeader column={column} title="Sample ID" />,
        accessorKey: "sample_id",
        enableSorting: true,
        cell: ({ getValue }) => (
          <span className="font-medium text-foreground">{getValue<string>()}</span>
        ),
      },
      {
        id: "study_identifier",
        header: ({ column }) => <SortableHeader column={column} title="Study ID" />,
        accessorFn: (row) => row.study_identifier?.name ?? "",
        enableSorting: true,
        cell: ({ row }) => formatMaybe(row.original.study_identifier?.name),
      },
      {
        header: ({ column }) => <SortableHeader column={column} title="Location" />,
        accessorKey: "sample_location",
        enableSorting: true,
        cell: ({ getValue }) => formatMaybe(getValue<string>()),
      },
      {
        header: ({ column }) => <SortableHeader column={column} title="Sublocation" />,
        accessorKey: "sample_sublocation",
        enableSorting: true,
        cell: ({ getValue }) => formatMaybe(getValue<string | null>()),
      },
      {
        header: ({ column }) => <SortableHeader column={column} title="Sample Type" />,
        accessorKey: "sample_type",
        enableSorting: true,
        cell: ({ row }) => (
          <span className="whitespace-normal break-words">
            {formatMaybe(row.original.sample_type_label ?? row.original.sample_type)}
          </span>
        ),
      },
      {
        header: ({ column }) => <SortableHeader column={column} title="Collected At" />,
        accessorKey: "sample_datetime",
        enableSorting: true,
        cell: ({ getValue }) => formatDate(getValue<string | null>()),
      },
      {
        header: "Timepoint",
        accessorKey: "timepoint_label",
        id: "timepoint_label",
        enableSorting: false,
        cell: ({ getValue }) => formatMaybe(getValue<string | null>()),
      },
      {
        header: "Group",
        accessorKey: "study_group_label",
        id: "study_group_label",
        enableSorting: false,
        cell: ({ getValue }) => formatMaybe(getValue<string | null>()),
      },
      {
        header: "Age",
        accessorKey: "age",
        id: "age",
        enableSorting: false,
        cell: ({ getValue }) => formatMaybe(getValue<number | null>()),
      },
      {
        header: "Sex",
        accessorKey: "sex_label",
        id: "sex_label",
        enableSorting: false,
        cell: ({ getValue }) => formatMaybe(getValue<string | null>()),
      },
      {
        header: "Center",
        accessorKey: "study_center_label",
        id: "study_center_label",
        enableSorting: false,
        cell: ({ getValue }) => formatMaybe(getValue<string | null>()),
      },
      {
        header: "CRP",
        accessorKey: "crp",
        id: "crp",
        enableSorting: false,
        cell: ({ getValue }) => formatNumber(getValue<number | null>()),
      },
      {
        header: "Calprotectin",
        accessorKey: "calprotectin",
        id: "calprotectin",
        enableSorting: false,
        cell: ({ getValue }) => formatNumber(getValue<number | null>()),
      },
      {
        header: "Mucosal Healing (3-6m)",
        accessorKey: "endoscopic_mucosal_healing_at_3_6_months",
        id: "endoscopic_mucosal_healing_at_3_6_months",
        enableSorting: false,
        cell: ({ getValue }) => formatBoolean(getValue<boolean | null>()),
      },
      {
        header: "Mucosal Healing (12m)",
        accessorKey: "endoscopic_mucosal_healing_at_12_months",
        id: "endoscopic_mucosal_healing_at_12_months",
        enableSorting: false,
        cell: ({ getValue }) => formatBoolean(getValue<boolean | null>()),
      },
      {
        header: "Genotyping",
        accessorKey: "genotype_data_available",
        id: "genotype_data_available",
        enableSorting: false,
        cell: ({ getValue }) => formatBoolean(getValue<boolean | null>()),
      },
      {
        header: "Comments",
        accessorKey: "sample_comments",
        enableSorting: false,
        cell: ({ getValue }) => formatMaybe(getValue<string | null>()),
      },
      {
        id: "actions",
        header: "Actions",
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex gap-2">
            <Link
              href={`/samples/${encodeURIComponent(row.original.sample_id)}`}
              className="flex items-center gap-1 text-primary underline"
              prefetch={false}
            >
              <Eye size={16} />
              View
            </Link>
            {row.original.id && (
              <a
                href={buildBackendUrl(`/samples/${row.original.id}/edit/`)}
                className="flex items-center gap-1 text-primary underline"
              >
                <Edit size={16} />
                Edit
              </a>
            )}
            {row.original.id && (
              <a
                href={buildBackendUrl(`/samples/${row.original.id}/used/`)}
                className="flex items-center gap-1 text-primary underline"
              >
                <Archive size={16} />
                Used
              </a>
            )}
          </div>
        ),
      },
    ];
  }, []);

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    pageCount,
    state: {
      pagination,
      columnVisibility,
      sorting,
    },
    manualPagination: true,
    manualSorting: true,
    onPaginationChange: setPagination,
    onColumnVisibilityChange: setColumnVisibility,
    onSortingChange: setSorting,
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading samples…</p>;
  }

  if (error) {
    return (
      <div className="rounded-md border border-destructive/50 bg-destructive/5 px-4 py-3 text-sm text-destructive">
        {error}
      </div>
    );
  }

  if (rows.length === 0) {
    return <p className="text-sm text-muted-foreground">No samples found.</p>;
  }

  const canPreviousPage = table.getCanPreviousPage();
  const canNextPage = table.getCanNextPage();
  const { pageIndex, pageSize } = pagination;
  const firstItemIndex = rows.length > 0 ? pageIndex * pageSize + 1 : 0;
  const lastItemIndex = rows.length > 0 ? pageIndex * pageSize + rows.length : 0;
  const totalLabel = totalCount ?? "unknown";

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Button variant="outline" size="sm" asChild>
            <a href="/api/dashboard/samples/export" target="_blank" rel="noreferrer">
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </a>
          </Button>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <Settings className="mr-2 h-4 w-4" />
              Columns
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuCheckboxItem
              checked={table.getColumn("timepoint_label")?.getIsVisible() ?? false}
              onCheckedChange={(value) =>
                table.getColumn("timepoint_label")?.toggleVisibility(value)
              }
            >
              Timepoint
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("study_group_label")?.getIsVisible() ?? false}
              onCheckedChange={(value) =>
                table.getColumn("study_group_label")?.toggleVisibility(value)
              }
            >
              Group
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("age")?.getIsVisible() ?? false}
              onCheckedChange={(value) => table.getColumn("age")?.toggleVisibility(value)}
            >
              Age
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("sex_label")?.getIsVisible() ?? false}
              onCheckedChange={(value) => table.getColumn("sex_label")?.toggleVisibility(value)}
            >
              Sex
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("study_center_label")?.getIsVisible() ?? false}
              onCheckedChange={(value) =>
                table.getColumn("study_center_label")?.toggleVisibility(value)
              }
            >
              Center
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("crp")?.getIsVisible() ?? false}
              onCheckedChange={(value) => table.getColumn("crp")?.toggleVisibility(value)}
            >
              CRP
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("calprotectin")?.getIsVisible() ?? false}
              onCheckedChange={(value) => table.getColumn("calprotectin")?.toggleVisibility(value)}
            >
              Calprotectin
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={
                table.getColumn("endoscopic_mucosal_healing_at_3_6_months")?.getIsVisible() ?? false
              }
              onCheckedChange={(value) =>
                table.getColumn("endoscopic_mucosal_healing_at_3_6_months")?.toggleVisibility(value)
              }
            >
              Mucosal Healing (3-6m)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={
                table.getColumn("endoscopic_mucosal_healing_at_12_months")?.getIsVisible() ?? false
              }
              onCheckedChange={(value) =>
                table.getColumn("endoscopic_mucosal_healing_at_12_months")?.toggleVisibility(value)
              }
            >
              Mucosal Healing (12m)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={table.getColumn("genotype_data_available")?.getIsVisible() ?? false}
              onCheckedChange={(value) =>
                table.getColumn("genotype_data_available")?.toggleVisibility(value)
              }
            >
              Genotyping
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <PaginationControls
        canPrevious={canPreviousPage}
        canNext={canNextPage}
        isLoading={isLoading}
        onPrevious={() => table.previousPage()}
        onNext={() => table.nextPage()}
        pageIndex={pageIndex}
        pageCount={pageCount}
        firstItemIndex={firstItemIndex}
        lastItemIndex={lastItemIndex}
        totalLabel={totalLabel}
      />
      <div className="max-w-full overflow-x-auto">
        <table className="w-full min-w-[1200px] table-auto border-collapse text-left text-sm">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-border/60">
                {headerGroup.headers.map((header) => (
                  <th key={header.id} className="px-3 py-2 font-semibold text-muted-foreground">
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="border-b border-border/40 last:border-none">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-3 py-2 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <PaginationControls
        canPrevious={canPreviousPage}
        canNext={canNextPage}
        isLoading={isLoading}
        onPrevious={() => table.previousPage()}
        onNext={() => table.nextPage()}
        pageIndex={pageIndex}
        pageCount={pageCount}
        firstItemIndex={firstItemIndex}
        lastItemIndex={lastItemIndex}
        totalLabel={totalLabel}
      />
    </div>
  );
}
