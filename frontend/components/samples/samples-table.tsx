// frontend/components/samples/samples-table.tsx
// Renders the landing-page samples table using TanStack Table and live backend data.
// Gives authenticated users a quick overview of recent samples pulled from the Django API.

"use client";

import { useEffect, useMemo, useState } from "react";
import {
  type ColumnDef,
  type PaginationState,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { Button } from "@/components/ui/button";

type SampleRow = {
  sample_id: string;
  study_name: string;
  sample_type: string;
  sample_datetime: string | null;
  sample_location: string | null;
  sample_sublocation: string | null;
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
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

const EMPTY_STATE: SampleRow[] = [];
const DEFAULT_PAGE_SIZE = 50;

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
        <Button variant="outline" size="sm" onClick={onPrevious} disabled={!canPrevious || isLoading}>
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
            ? (payload as SampleApiPayload).count ?? 0
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
  }, [pagination]);

  const columns = useMemo<ColumnDef<SampleRow>[]>(() => {
    return [
      {
        header: "Sample ID",
        accessorKey: "sample_id",
        cell: ({ getValue }) => <span className="font-medium text-foreground">{getValue<string>()}</span>,
      },
      {
        header: "Study",
        accessorKey: "study_name",
        cell: ({ getValue }) => getValue<string>() ?? "—",
      },
      {
        header: "Type",
        accessorKey: "sample_type",
        cell: ({ getValue }) => getValue<string>() ?? "—",
      },
      {
        header: "Collected",
        accessorKey: "sample_datetime",
        cell: ({ getValue }) => {
          const value = getValue<string | null>();
          if (!value) {
            return "—";
          }
          const date = new Date(value);
          if (Number.isNaN(date.getTime())) {
            return value;
          }
          return dateFormatter.format(date);
        },
      },
      {
        header: "Location",
        accessorFn: (row) => {
          const pieces = [row.sample_location, row.sample_sublocation].filter(Boolean);
          return pieces.length > 0 ? pieces.join(" · ") : null;
        },
        cell: ({ getValue }) => getValue<string | null>() ?? "—",
      },
      {
        header: "Status",
        accessorKey: "is_used",
        cell: ({ getValue }) => (getValue<boolean>() ? "Used" : "Available"),
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
    },
    manualPagination: true,
    onPaginationChange: setPagination,
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
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] table-fixed border-collapse text-left text-sm">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-border/60">
                {headerGroup.headers.map((header) => (
                  <th key={header.id} className="px-3 py-2 font-semibold text-muted-foreground">
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="border-b border-border/40 last:border-none">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-3 py-2">
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
