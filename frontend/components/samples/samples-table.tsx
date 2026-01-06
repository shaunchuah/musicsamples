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
  CheckSquare,
  Download,
  Edit,
  Eye,
  Filter,
  Settings,
  Square,
  X,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useId, useMemo, useState } from "react";

import { AlertDescription, AlertError, AlertSuccess, AlertWarning } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TablePagination } from "@/components/ui/table-pagination";
import { dateFormatter, timeFormatter } from "@/lib/formatters";

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

type FilterOption = {
  value: string;
  label: string;
};

type SampleFilterOptions = {
  study_name: FilterOption[];
  sample_type: FilterOption[];
  study_group: FilterOption[];
  study_center: FilterOption[];
  sex: FilterOption[];
  music_timepoint: FilterOption[];
  marvel_timepoint: FilterOption[];
  biopsy_location: FilterOption[];
  biopsy_inflamed_status: FilterOption[];
  boolean: FilterOption[];
};

type SampleFilters = {
  study_name: string;
  sample_type: string;
  study_id__name: string;
  sample_location: string;
  sample_sublocation: string;
  sample_comments: string;
  sample_datetime_after: string;
  sample_datetime_before: string;
  is_used: string;
  study_id__study_group: string;
  study_id__study_center: string;
  study_id__sex: string;
  study_id__genotype_data_available: string;
  study_id__nod2_mutation_present: string;
  study_id__il23r_mutation_present: string;
  endoscopic_mucosal_healing_at_3_6_months: string;
  endoscopic_mucosal_healing_at_12_months: string;
  music_timepoint: string;
  marvel_timepoint: string;
  biopsy_location: string;
  biopsy_inflamed_status: string;
};

const EMPTY_STATE: SampleRow[] = [];
const DEFAULT_PAGE_SIZE = 50;
const EMPTY_SELECT_VALUE = "__none__";
const DEFAULT_FILTERS: SampleFilters = {
  study_name: "",
  sample_type: "",
  study_id__name: "",
  sample_location: "",
  sample_sublocation: "",
  sample_comments: "",
  sample_datetime_after: "",
  sample_datetime_before: "",
  is_used: "",
  study_id__study_group: "",
  study_id__study_center: "",
  study_id__sex: "",
  study_id__genotype_data_available: "",
  study_id__nod2_mutation_present: "",
  study_id__il23r_mutation_present: "",
  endoscopic_mucosal_healing_at_3_6_months: "",
  endoscopic_mucosal_healing_at_12_months: "",
  music_timepoint: "",
  marvel_timepoint: "",
  biopsy_location: "",
  biopsy_inflamed_status: "",
};
const DEFAULT_BOOLEAN_OPTIONS: FilterOption[] = [
  { value: "true", label: "Yes" },
  { value: "false", label: "No" },
];

const SORT_FIELD_MAP: Record<string, string> = {
  study_name: "study_name",
  sample_id: "sample_id",
  study_identifier: "study_id__name",
  sample_location: "sample_location",
  sample_sublocation: "sample_sublocation",
  sample_type: "sample_type",
  sample_datetime: "sample_datetime",
};

const SORT_LABELS: Record<string, string> = {
  study_name: "Study",
  sample_id: "Sample ID",
  study_identifier: "Study ID",
  sample_location: "Location",
  sample_sublocation: "Sublocation",
  sample_type: "Sample Type",
  sample_datetime: "Collected at",
};

const TABLE_HEADER_CLASS =
  "px-3 py-2 text-sm font-semibold normal-case tracking-normal text-muted-foreground";

const FILTER_LABELS: Record<keyof SampleFilters, string> = {
  study_name: "Study name",
  sample_type: "Sample type",
  study_id__name: "Study ID",
  sample_location: "Location",
  sample_sublocation: "Sublocation",
  sample_comments: "Comments contain",
  sample_datetime_after: "Collected after",
  sample_datetime_before: "Collected before",
  is_used: "Used samples",
  study_id__study_group: "Study group",
  study_id__study_center: "Study center",
  study_id__sex: "Biological sex",
  study_id__genotype_data_available: "Genotype data available",
  study_id__nod2_mutation_present: "NOD2 mutation present",
  study_id__il23r_mutation_present: "IL23R mutation present",
  endoscopic_mucosal_healing_at_3_6_months: "Mucosal healing (3-6m)",
  endoscopic_mucosal_healing_at_12_months: "Mucosal healing (12m)",
  music_timepoint: "Music timepoint",
  marvel_timepoint: "Marvel timepoint",
  biopsy_location: "Biopsy location",
  biopsy_inflamed_status: "Biopsy inflamed status",
};

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

function getFilterFieldClass(baseClass: string, value: string): string {
  if (!value.trim()) {
    return baseClass;
  }
  return `${baseClass} border-primary/70 bg-primary/5 ring-1 ring-primary/30`;
}

export function SamplesTable() {
  const [rows, setRows] = useState<SampleRow[]>(EMPTY_STATE);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usedDialogOpen, setUsedDialogOpen] = useState(false);
  const [usedTarget, setUsedTarget] = useState<SampleRow | null>(null);
  const [usedError, setUsedError] = useState<string | null>(null);
  const [isMarkingUsed, setIsMarkingUsed] = useState(false);
  const [usedStatusMessage, setUsedStatusMessage] = useState<string | null>(null);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [includeUsed, setIncludeUsed] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filterOptions, setFilterOptions] = useState<SampleFilterOptions | null>(null);
  const [filters, setFilters] = useState<SampleFilters>(DEFAULT_FILTERS);
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
  const studyIdInputId = useId();
  const sampleLocationInputId = useId();
  const sampleSublocationInputId = useId();
  const collectedAfterInputId = useId();
  const collectedBeforeInputId = useId();
  const commentsInputId = useId();
  const filterSelectIdPrefix = useId();

  const activeFilterCount = useMemo(() => {
    return Object.values(filters).filter((value) => value.trim() !== "").length;
  }, [filters]);

  const orderingValues = useMemo(() => {
    return sorting
      .map(({ id, desc }) => {
        const field = SORT_FIELD_MAP[id];
        if (!field) {
          return null;
        }
        return `${desc ? "-" : ""}${field}`;
      })
      .filter((value): value is string => Boolean(value));
  }, [sorting]);

  const orderingLabels = useMemo(() => {
    return sorting
      .map(({ id, desc }) => {
        const label = SORT_LABELS[id] ?? id;
        return `${label} (${desc ? "descending" : "ascending"})`;
      })
      .filter((value) => value.trim() !== "");
  }, [sorting]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setPagination((previous) => {
      if (previous.pageIndex === 0) {
        return previous;
      }
      return { ...previous, pageIndex: 0 };
    });
  }, [sorting, searchQuery, includeUsed, filters]);

  useEffect(() => {
    if (!usedStatusMessage) {
      return;
    }

    const timer = window.setTimeout(() => {
      setUsedStatusMessage(null);
    }, 3000);

    return () => window.clearTimeout(timer);
  }, [usedStatusMessage]);

  const buildSamplesQueryParams = () => {
    const query = new URLSearchParams();

    if (orderingValues.length > 0) {
      query.set("ordering", orderingValues.join(","));
    }

    if (includeUsed) {
      query.set("include_used", "true");
    }

    Object.entries(filters).forEach(([key, value]) => {
      const trimmedValue = value.trim();
      if (trimmedValue) {
        query.set(key, trimmedValue);
      }
    });

    if (searchQuery) {
      query.set("query", searchQuery);
    }

    return query;
  };

  useEffect(() => {
    const controller = new AbortController();

    async function loadFilterOptions() {
      try {
        const response = await fetch("/api/dashboard/samples/filters", {
          signal: controller.signal,
        });

        if (!response.ok) {
          return;
        }

        const payload = (await response.json()) as SampleFilterOptions;
        setFilterOptions(payload);
      } catch {
        if (!controller.signal.aborted) {
          setFilterOptions(null);
        }
      }
    }

    loadFilterOptions();

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadSamples() {
      setIsLoading(true);
      setError(null);
      setRows(EMPTY_STATE);

      try {
        const { pageIndex, pageSize } = pagination;
        const query = buildSamplesQueryParams();
        query.set("page", String(pageIndex + 1));
        query.set("page_size", String(pageSize));

        const endpoint = searchQuery ? "/api/dashboard/samples/search" : "/api/dashboard/samples";

        const response = await fetch(`${endpoint}?${query.toString()}`, {
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
  }, [pagination, sorting, searchQuery, includeUsed, filters]);

  const closeUsedDialog = (forceClose = false) => {
    if (isMarkingUsed && !forceClose) {
      return;
    }
    setUsedDialogOpen(false);
    setUsedTarget(null);
    setUsedError(null);
  };

  const openUsedDialog = (row: SampleRow) => {
    setUsedTarget(row);
    setUsedError(null);
    setUsedDialogOpen(true);
  };

  const handleUsedDialogChange = (open: boolean) => {
    if (!open) {
      closeUsedDialog();
      return;
    }
    setUsedDialogOpen(true);
  };

  const handleConfirmUsed = async () => {
    if (!usedTarget) {
      return;
    }

    setIsMarkingUsed(true);
    setUsedError(null);

    try {
      const response = await fetch("/api/dashboard/qr-scan/mark-used", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sample_id: usedTarget.sample_id }),
      });

      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        let errorDetail = "Unable to mark sample as used.";
        if (payload && typeof payload === "object" && !Array.isArray(payload)) {
          const payloadRecord = payload as Record<string, unknown>;
          if (typeof payloadRecord.detail === "string") {
            errorDetail = payloadRecord.detail;
          }
          if (typeof payloadRecord.error === "string") {
            errorDetail = payloadRecord.error;
          }
        } else if (typeof payload === "string") {
          errorDetail = payload;
        }
        setUsedError(errorDetail);
        return;
      }

      setRows((previous) => previous.filter((row) => row.sample_id !== usedTarget.sample_id));
      setTotalCount((previous) => {
        if (typeof previous !== "number") {
          return previous;
        }
        const nextTotal = Math.max(previous - 1, 0);
        setPageCount(nextTotal > 0 ? Math.ceil(nextTotal / pagination.pageSize) : 1);
        return nextTotal;
      });
      setUsedStatusMessage(`Sample ${usedTarget.sample_id} marked as used.`);
      closeUsedDialog(true);
    } catch {
      setUsedError("Something went wrong. Please try again.");
    } finally {
      setIsMarkingUsed(false);
    }
  };

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
            <Button asChild variant="link" size="sm" className="h-auto p-0">
              <Link
                href={`/samples/${encodeURIComponent(row.original.sample_id)}`}
                prefetch={false}
              >
                <Eye size={16} />
                View
              </Link>
            </Button>
            <Button asChild variant="link" size="sm" className="h-auto p-0">
              <Link
                href={`/samples/${encodeURIComponent(row.original.sample_id)}/edit?from=dashboard`}
                prefetch={false}
              >
                <Edit size={16} />
                Edit
              </Link>
            </Button>
            <Button
              type="button"
              variant="link"
              size="sm"
              className="h-auto p-0"
              onClick={() => openUsedDialog(row.original)}
              disabled={row.original.is_used || isMarkingUsed}
            >
              <Archive size={16} />
              {row.original.is_used ? "Used" : "Mark used"}
            </Button>
          </div>
        ),
      },
    ];
  }, [isMarkingUsed]);

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

  const columnToggleIds = [
    "timepoint_label",
    "study_group_label",
    "age",
    "sex_label",
    "study_center_label",
    "crp",
    "calprotectin",
    "endoscopic_mucosal_healing_at_3_6_months",
    "endoscopic_mucosal_healing_at_12_months",
    "genotype_data_available",
  ];

  const showAllColumns = () => {
    for (const columnId of columnToggleIds) {
      table.getColumn(columnId)?.toggleVisibility(true);
    }
  };

  const hideAllColumns = () => {
    for (const columnId of columnToggleIds) {
      table.getColumn(columnId)?.toggleVisibility(false);
    }
  };

  const canPreviousPage = table.getCanPreviousPage();
  const canNextPage = table.getCanNextPage();
  const { pageIndex, pageSize } = pagination;
  const booleanOptions = filterOptions?.boolean ?? DEFAULT_BOOLEAN_OPTIONS;
  const hasExportConstraints = searchQuery.trim() !== "" || activeFilterCount > 0 || includeUsed;

  const filterOptionLookup: Partial<Record<keyof SampleFilters, FilterOption[]>> = useMemo(
    () => ({
      study_name: filterOptions?.study_name ?? [],
      sample_type: filterOptions?.sample_type ?? [],
      study_id__name: [],
      is_used: booleanOptions,
      study_id__study_group: filterOptions?.study_group ?? [],
      study_id__study_center: filterOptions?.study_center ?? [],
      study_id__sex: filterOptions?.sex ?? [],
      study_id__genotype_data_available: booleanOptions,
      study_id__nod2_mutation_present: booleanOptions,
      study_id__il23r_mutation_present: booleanOptions,
      endoscopic_mucosal_healing_at_3_6_months: booleanOptions,
      endoscopic_mucosal_healing_at_12_months: booleanOptions,
      music_timepoint: filterOptions?.music_timepoint ?? [],
      marvel_timepoint: filterOptions?.marvel_timepoint ?? [],
      biopsy_location: filterOptions?.biopsy_location ?? [],
      biopsy_inflamed_status: filterOptions?.biopsy_inflamed_status ?? [],
    }),
    [filterOptions, booleanOptions],
  );

  const exportParams = useMemo(() => {
    const params: Array<{ label: string; value: string }> = [];

    if (searchQuery.trim()) {
      params.push({ label: "Search", value: searchQuery.trim() });
    }

    if (includeUsed) {
      params.push({ label: "Include used samples", value: "Yes" });
    }

    Object.entries(filters).forEach(([key, value]) => {
      const trimmedValue = value.trim();
      if (!trimmedValue) {
        return;
      }

      const options = filterOptionLookup[key as keyof SampleFilters];
      const resolvedValue = options?.find(
        (option: FilterOption) => option.value === trimmedValue,
      )?.label;
      params.push({
        label: FILTER_LABELS[key as keyof SampleFilters] ?? key,
        value: resolvedValue ?? trimmedValue,
      });
    });

    if (orderingLabels.length > 0) {
      params.push({ label: "Ordering", value: orderingLabels.join(", ") });
    }

    return params;
  }, [filters, searchQuery, includeUsed, filterOptionLookup, orderingLabels]);

  const buildExportUrl = () => {
    const query = buildSamplesQueryParams();
    const queryString = query.toString();
    return queryString
      ? `/api/dashboard/samples/export?${queryString}`
      : "/api/dashboard/samples/export";
  };

  const handleExportConfirm = () => {
    const exportUrl = buildExportUrl();
    window.open(exportUrl, "_blank", "noopener,noreferrer");
    setExportDialogOpen(false);
  };

  return (
    <div className="flex flex-col gap-4">
      {usedStatusMessage ? (
        <AlertSuccess>
          <AlertDescription>{usedStatusMessage}</AlertDescription>
        </AlertSuccess>
      ) : null}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search samples..."
              className="h-9 w-64 pr-8"
            />
            <button
              type="button"
              className={`absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground transition hover:text-foreground disabled:opacity-40${searchInput ? " cursor-pointer" : ""}`}
              onClick={() => {
                setSearchInput("");
                setSearchQuery("");
              }}
              disabled={!searchInput}
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-input text-primary"
              checked={includeUsed}
              onChange={(event) => setIncludeUsed(event.target.checked)}
            />
            Include used samples?
          </label>
        </div>
        <div className="flex items-center gap-2">
          {activeFilterCount > 0 ? (
            <Button
              variant="secondary"
              size="sm"
              type="button"
              onClick={() => {
                setFilters(DEFAULT_FILTERS);
                setFiltersOpen(false);
              }}
            >
              <X className="mr-2 h-4 w-4" />
              Clear
            </Button>
          ) : null}
          <Button
            variant={filtersOpen ? "default" : "outline"}
            size="sm"
            type="button"
            onClick={() => setFiltersOpen((previous) => !previous)}
            aria-expanded={filtersOpen}
            className="relative"
          >
            <Filter className="mr-2 h-4 w-4" />
            Filters
            {activeFilterCount > 0 ? (
              <span className="ml-2 rounded-full bg-primary px-1.5 py-0.5 text-[10px] font-semibold text-primary-foreground">
                {activeFilterCount}
              </span>
            ) : null}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Settings className="mr-2 h-4 w-4" />
                Columns
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onSelect={(event) => {
                  event.preventDefault();
                  showAllColumns();
                }}
              >
                <CheckSquare className="h-4 w-4" />
                Select all
              </DropdownMenuItem>
              <DropdownMenuItem
                onSelect={(event) => {
                  event.preventDefault();
                  hideAllColumns();
                }}
              >
                <Square className="h-4 w-4" />
                Unselect all
              </DropdownMenuItem>
              <DropdownMenuSeparator />
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
                onCheckedChange={(value) =>
                  table.getColumn("calprotectin")?.toggleVisibility(value)
                }
              >
                Calprotectin
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={
                  table.getColumn("endoscopic_mucosal_healing_at_3_6_months")?.getIsVisible() ??
                  false
                }
                onCheckedChange={(value) =>
                  table
                    .getColumn("endoscopic_mucosal_healing_at_3_6_months")
                    ?.toggleVisibility(value)
                }
              >
                Mucosal Healing (3-6m)
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={
                  table.getColumn("endoscopic_mucosal_healing_at_12_months")?.getIsVisible() ??
                  false
                }
                onCheckedChange={(value) =>
                  table
                    .getColumn("endoscopic_mucosal_healing_at_12_months")
                    ?.toggleVisibility(value)
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
          <Button
            variant="outline"
            size="sm"
            type="button"
            onClick={() => setExportDialogOpen(true)}
          >
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <div
        className={`overflow-hidden rounded-md border border-border/60 bg-muted/20 transition-all duration-300 ease-out${
          filtersOpen ? " max-h-[1200px] p-4 opacity-100" : " max-h-0 p-0 opacity-0"
        }`}
      >
        <div className={filtersOpen ? "" : "pointer-events-none"}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm font-medium text-foreground">Filters</p>
            <Button
              variant="ghost"
              size="sm"
              type="button"
              onClick={() => setFiltersOpen(false)}
              aria-label="Close filters"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="mt-3 grid gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-study-name`}
            >
              Study name
              <Select
                value={filters.study_name || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_name: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_name,
                  )}
                  id={`${filterSelectIdPrefix}-study-name`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.study_name ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-sample-type`}
            >
              Sample type
              <Select
                value={filters.sample_type || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    sample_type: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.sample_type,
                  )}
                  id={`${filterSelectIdPrefix}-sample-type`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.sample_type ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={studyIdInputId}
            >
              Study ID
              <Input
                id={studyIdInputId}
                value={filters.study_id__name}
                onChange={(event) =>
                  setFilters((previous) => ({ ...previous, study_id__name: event.target.value }))
                }
                placeholder="e.g. MUSIC-001"
                className={getFilterFieldClass("h-9", filters.study_id__name)}
              />
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={sampleLocationInputId}
            >
              Location
              <Input
                id={sampleLocationInputId}
                value={filters.sample_location}
                onChange={(event) =>
                  setFilters((previous) => ({
                    ...previous,
                    sample_location: event.target.value,
                  }))
                }
                placeholder="e.g. Freezer 1"
                className={getFilterFieldClass("h-9", filters.sample_location)}
              />
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={sampleSublocationInputId}
            >
              Sublocation
              <Input
                id={sampleSublocationInputId}
                value={filters.sample_sublocation}
                onChange={(event) =>
                  setFilters((previous) => ({
                    ...previous,
                    sample_sublocation: event.target.value,
                  }))
                }
                placeholder="e.g. Rack A"
                className={getFilterFieldClass("h-9", filters.sample_sublocation)}
              />
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-used-samples`}
            >
              Used samples
              <Select
                value={filters.is_used || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    is_used: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.is_used,
                  )}
                  id={`${filterSelectIdPrefix}-used-samples`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {booleanOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={collectedAfterInputId}
            >
              Collected after
              <Input
                id={collectedAfterInputId}
                type="date"
                value={filters.sample_datetime_after}
                onChange={(event) =>
                  setFilters((previous) => ({
                    ...previous,
                    sample_datetime_after: event.target.value,
                  }))
                }
                className={getFilterFieldClass("h-9", filters.sample_datetime_after)}
              />
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={collectedBeforeInputId}
            >
              Collected before
              <Input
                id={collectedBeforeInputId}
                type="date"
                value={filters.sample_datetime_before}
                onChange={(event) =>
                  setFilters((previous) => ({
                    ...previous,
                    sample_datetime_before: event.target.value,
                  }))
                }
                className={getFilterFieldClass("h-9", filters.sample_datetime_before)}
              />
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={commentsInputId}
            >
              Comments contain
              <Input
                id={commentsInputId}
                value={filters.sample_comments}
                onChange={(event) =>
                  setFilters((previous) => ({
                    ...previous,
                    sample_comments: event.target.value,
                  }))
                }
                className={getFilterFieldClass("h-9", filters.sample_comments)}
              />
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-study-group`}
            >
              Study group
              <Select
                value={filters.study_id__study_group || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_id__study_group: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_id__study_group,
                  )}
                  id={`${filterSelectIdPrefix}-study-group`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.study_group ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-study-center`}
            >
              Study center
              <Select
                value={filters.study_id__study_center || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_id__study_center: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_id__study_center,
                  )}
                  id={`${filterSelectIdPrefix}-study-center`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.study_center ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-biological-sex`}
            >
              Biological sex
              <Select
                value={filters.study_id__sex || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_id__sex: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_id__sex,
                  )}
                  id={`${filterSelectIdPrefix}-biological-sex`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.sex ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-genotype`}
            >
              Genotype data available
              <Select
                value={filters.study_id__genotype_data_available || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_id__genotype_data_available: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_id__genotype_data_available,
                  )}
                  id={`${filterSelectIdPrefix}-genotype`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {booleanOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-nod2`}
            >
              NOD2 mutation present
              <Select
                value={filters.study_id__nod2_mutation_present || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_id__nod2_mutation_present: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_id__nod2_mutation_present,
                  )}
                  id={`${filterSelectIdPrefix}-nod2`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {booleanOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-il23r`}
            >
              IL23R mutation present
              <Select
                value={filters.study_id__il23r_mutation_present || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    study_id__il23r_mutation_present: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.study_id__il23r_mutation_present,
                  )}
                  id={`${filterSelectIdPrefix}-il23r`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {booleanOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-healing-3-6`}
            >
              Mucosal healing (3-6m)
              <Select
                value={filters.endoscopic_mucosal_healing_at_3_6_months || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    endoscopic_mucosal_healing_at_3_6_months:
                      value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.endoscopic_mucosal_healing_at_3_6_months,
                  )}
                  id={`${filterSelectIdPrefix}-healing-3-6`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {booleanOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-healing-12`}
            >
              Mucosal healing (12m)
              <Select
                value={filters.endoscopic_mucosal_healing_at_12_months || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    endoscopic_mucosal_healing_at_12_months:
                      value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.endoscopic_mucosal_healing_at_12_months,
                  )}
                  id={`${filterSelectIdPrefix}-healing-12`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {booleanOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-music-timepoint`}
            >
              Music timepoint
              <Select
                value={filters.music_timepoint || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    music_timepoint: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.music_timepoint,
                  )}
                  id={`${filterSelectIdPrefix}-music-timepoint`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.music_timepoint ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-marvel-timepoint`}
            >
              Marvel timepoint
              <Select
                value={filters.marvel_timepoint || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    marvel_timepoint: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.marvel_timepoint,
                  )}
                  id={`${filterSelectIdPrefix}-marvel-timepoint`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.marvel_timepoint ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-biopsy-location`}
            >
              Biopsy location
              <Select
                value={filters.biopsy_location || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    biopsy_location: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.biopsy_location,
                  )}
                  id={`${filterSelectIdPrefix}-biopsy-location`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.biopsy_location ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label
              className="flex flex-col gap-1 text-xs text-muted-foreground"
              htmlFor={`${filterSelectIdPrefix}-biopsy-status`}
            >
              Biopsy inflamed status
              <Select
                value={filters.biopsy_inflamed_status || EMPTY_SELECT_VALUE}
                onValueChange={(value) =>
                  setFilters((previous) => ({
                    ...previous,
                    biopsy_inflamed_status: value === EMPTY_SELECT_VALUE ? "" : value,
                  }))
                }
              >
                <SelectTrigger
                  className={getFilterFieldClass(
                    "h-9 w-full text-sm text-foreground",
                    filters.biopsy_inflamed_status,
                  )}
                  id={`${filterSelectIdPrefix}-biopsy-status`}
                >
                  <SelectValue placeholder="Any" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                  {(filterOptions?.biopsy_inflamed_status ?? []).map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
          </div>
          <div className="mt-3 flex justify-start">
            <Button
              variant="outline"
              size="sm"
              type="button"
              onClick={() => setFilters(DEFAULT_FILTERS)}
            >
              Clear filters
            </Button>
          </div>
        </div>
      </div>

      <TablePagination
        canPrevious={canPreviousPage}
        canNext={canNextPage}
        isLoading={isLoading}
        onPrevious={() => table.previousPage()}
        onNext={() => table.nextPage()}
        pageIndex={pageIndex + 1}
        pageCount={pageCount}
        pageSize={pageSize}
        currentCount={rows.length}
        totalCount={totalCount}
        itemLabel="samples"
      />
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading samples…</p>
      ) : error ? (
        <div className="rounded-md border border-destructive/50 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      ) : rows.length === 0 ? (
        <p className="text-sm text-muted-foreground">No samples found.</p>
      ) : (
        <Table className="min-w-[1200px] table-auto [&_td]:px-3 [&_td]:py-2">
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-b border-border/60">
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className={TABLE_HEADER_CLASS}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id} className="border-b border-border/40 last:border-none">
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id} className="whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
      <TablePagination
        canPrevious={canPreviousPage}
        canNext={canNextPage}
        isLoading={isLoading}
        onPrevious={() => table.previousPage()}
        onNext={() => table.nextPage()}
        pageIndex={pageIndex + 1}
        pageCount={pageCount}
        pageSize={pageSize}
        currentCount={rows.length}
        totalCount={totalCount}
        itemLabel="samples"
      />
      <Dialog open={exportDialogOpen} onOpenChange={setExportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Export CSV</DialogTitle>
            <DialogDescription>
              Review the parameters that will be applied to this export.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <div className="flex flex-col gap-1 text-sm sm:flex-row sm:items-center sm:gap-4">
              <span className="min-w-[160px] text-muted-foreground">Samples to export</span>
              <span className="font-semibold text-foreground">
                {typeof totalCount === "number" ? totalCount : "Unknown"}
              </span>
            </div>
            {!hasExportConstraints ? (
              <AlertWarning>
                <AlertDescription>
                  No search or filters are applied. You are about to export the entire dataset,
                  which may take some time.
                </AlertDescription>
              </AlertWarning>
            ) : null}
            {exportParams.length > 0 ? (
              <div className="space-y-2 text-sm">
                {exportParams.map((param) => (
                  <div
                    key={`${param.label}-${param.value}`}
                    className="flex flex-col gap-1 sm:flex-row sm:items-start sm:gap-4"
                  >
                    <span className="min-w-[160px] text-muted-foreground">{param.label}</span>
                    <span className="font-medium text-foreground break-words sm:flex-1">
                      {param.value}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No search or filters are applied.</p>
            )}
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setExportDialogOpen(false)}>
              Cancel
            </Button>
            <Button type="button" onClick={handleExportConfirm}>
              Confirm export
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog open={usedDialogOpen} onOpenChange={handleUsedDialogChange}>
        <DialogContent showCloseButton={!isMarkingUsed}>
          <DialogHeader>
            <DialogTitle>Mark sample as used?</DialogTitle>
            <DialogDescription>
              This will update sample{" "}
              <span className="font-semibold text-foreground">{usedTarget?.sample_id ?? "—"}</span>{" "}
              to used. You can restore it from the legacy views if needed.
            </DialogDescription>
          </DialogHeader>
          {usedError ? (
            <AlertError>
              <AlertDescription>{usedError}</AlertDescription>
            </AlertError>
          ) : null}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => closeUsedDialog()}
              disabled={isMarkingUsed}
            >
              Cancel
            </Button>
            <Button type="button" onClick={handleConfirmUsed} disabled={isMarkingUsed} variant="destructive">
              {isMarkingUsed ? "Marking..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
