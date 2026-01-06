// frontend/components/experiments/experiments-table.tsx
// Renders the experiments dashboard table with search, export, and pagination controls.
// Exists to mirror the legacy Django experiment list in the Next.js dashboard.

"use client";

import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Download,
  Edit,
  Eye,
  Filter,
  RotateCcw,
  Trash2,
  X,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useId, useMemo, useState } from "react";

import { ExperimentFormDialog } from "@/components/experiments/experiment-form-dialog";
import { AlertDescription, AlertError, AlertWarning } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import { dateFormatter } from "@/lib/formatters";

type ExperimentBoxSummary = {
  id: number;
  box_id: string;
};

type ExperimentRow = {
  id: number;
  date: string | null;
  basic_science_group: string;
  basic_science_group_label: string | null;
  name: string;
  description: string | null;
  sample_types: number[];
  sample_type_labels: string[];
  tissue_types: number[];
  tissue_type_labels: string[];
  species: string;
  species_label: string | null;
  boxes: ExperimentBoxSummary[];
  created: string | null;
  created_by_email: string | null;
  is_deleted: boolean;
};

type ExperimentApiPayload = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: ExperimentRow[];
};

type SortKey = "date" | "basic_science_group" | "name" | "created";

const DEFAULT_PAGE_SIZE = 20;
const EMPTY_SELECT_VALUE = "__none__";
const DEFAULT_BOOLEAN_OPTIONS: FilterOption[] = [
  { value: "true", label: "Yes" },
  { value: "false", label: "No" },
];

const SORT_FIELD_MAP: Record<SortKey, string> = {
  date: "date",
  basic_science_group: "basic_science_group",
  name: "name",
  created: "created",
};

const SORT_LABELS: Record<SortKey, string> = {
  date: "Date",
  basic_science_group: "Group",
  name: "Name",
  created: "Created",
};

type SortState = {
  id: SortKey;
  desc: boolean;
} | null;

const TABLE_HEADER_CLASS =
  "px-3 py-2 text-sm font-semibold normal-case tracking-normal text-muted-foreground";

type FilterOption = {
  value: string;
  label: string;
};

type ExperimentFilterOptions = {
  basic_science_group: FilterOption[];
  species: FilterOption[];
  sample_types: FilterOption[];
  tissue_types: FilterOption[];
  boolean: FilterOption[];
};

type ExperimentFilters = {
  basic_science_group: string;
  species: string;
  sample_types: string;
  tissue_types: string;
  date_after: string;
  date_before: string;
  is_deleted: string;
};

const DEFAULT_FILTERS: ExperimentFilters = {
  basic_science_group: "",
  species: "",
  sample_types: "",
  tissue_types: "",
  date_after: "",
  date_before: "",
  is_deleted: "",
};

const FILTER_LABELS: Record<keyof ExperimentFilters, string> = {
  basic_science_group: "Basic science group",
  species: "Species",
  sample_types: "Sample types",
  tissue_types: "Tissue types",
  date_after: "Experiment date after",
  date_before: "Experiment date before",
  is_deleted: "Deleted experiments",
};

function getFilterFieldClass(baseClass: string, value: string): string {
  if (!value.trim()) {
    return baseClass;
  }
  return `${baseClass} border-primary/70 bg-primary/5 ring-1 ring-primary/30`;
}

type SortIndicatorProps = {
  state: "asc" | "desc" | false;
};

type SortableHeaderProps = {
  title: string;
  sortKey: SortKey;
  state: "asc" | "desc" | false;
  onToggle: (key: SortKey) => void;
};

function SortIndicator({ state }: SortIndicatorProps) {
  if (!state) {
    return <ArrowUpDown className="h-3 w-3 text-muted-foreground" />;
  }
  if (state === "asc") {
    return <ArrowUp className="h-3 w-3 text-muted-foreground" />;
  }
  return <ArrowDown className="h-3 w-3 text-muted-foreground" />;
}

function SortableHeader({ title, sortKey, state, onToggle }: SortableHeaderProps) {
  return (
    <button
      type="button"
      className="flex items-center gap-1 focus-visible:outline-none focus-visible:ring-0"
      onClick={() => onToggle(sortKey)}
    >
      <span>{title}</span>
      <SortIndicator state={state} />
    </button>
  );
}
function formatDate(dateValue: string | null) {
  if (!dateValue) {
    return "";
  }
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return dateFormatter.format(date);
}

function formatList(values: string[]) {
  if (!values.length) {
    return "N/A";
  }
  return values.join(", ");
}

export function ExperimentsTable() {
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filterOptions, setFilterOptions] = useState<ExperimentFilterOptions | null>(null);
  const [filters, setFilters] = useState<ExperimentFilters>(DEFAULT_FILTERS);
  const [pageIndex, setPageIndex] = useState(1);
  const [sorting, setSorting] = useState<SortState>({ id: "date", desc: true });
  const [experiments, setExperiments] = useState<ExperimentRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [activeExperiment, setActiveExperiment] = useState<ExperimentRow | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<ExperimentRow | null>(null);
  const [deleteAction, setDeleteAction] = useState<"delete" | "restore">("delete");
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);
  const filterSelectIdPrefix = useId();

  const canPrevious = pageIndex > 1;
  const canNext = pageIndex * DEFAULT_PAGE_SIZE < totalCount;
  const pageCount = totalCount > 0 ? Math.ceil(totalCount / DEFAULT_PAGE_SIZE) : 0;

  const activeFilterCount = useMemo(() => {
    return Object.values(filters).filter((value) => value.trim() !== "").length;
  }, [filters]);

  const orderingValue = useMemo(() => {
    if (!sorting) {
      return "";
    }
    const field = SORT_FIELD_MAP[sorting.id];
    if (!field) {
      return "";
    }
    return `${sorting.desc ? "-" : ""}${field}`;
  }, [sorting]);

  const orderingLabel = useMemo(() => {
    if (!sorting) {
      return "";
    }
    const label = SORT_LABELS[sorting.id] ?? sorting.id;
    return `${label} (${sorting.desc ? "descending" : "ascending"})`;
  }, [sorting]);

  const buildExperimentsQueryParams = useCallback(() => {
    const params = new URLSearchParams();
    if (searchQuery) {
      params.set("query", searchQuery);
    }
    if (includeDeleted) {
      params.set("include_deleted", "true");
    }
    if (orderingValue) {
      params.set("ordering", orderingValue);
    }
    Object.entries(filters).forEach(([key, value]) => {
      const trimmedValue = value.trim();
      if (trimmedValue) {
        params.set(key, trimmedValue);
      }
    });
    return params;
  }, [filters, includeDeleted, orderingValue, searchQuery]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setPageIndex((previous) => (previous === 1 ? previous : 1));
  }, [includeDeleted, searchQuery, sorting, filters]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadFilterOptions() {
      try {
        const response = await fetch("/api/dashboard/experiments/filters", {
          signal: controller.signal,
        });
        if (!response.ok) {
          return;
        }
        const payload = (await response.json()) as ExperimentFilterOptions;
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
    let isActive = true;

    const loadExperiments = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const params = buildExperimentsQueryParams();
        params.set("page", String(pageIndex));
        params.set("page_size", String(DEFAULT_PAGE_SIZE));

        const response = await fetch(`/api/dashboard/experiments/search?${params.toString()}`, {
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error("Unable to load experiments.");
        }
        const payload = (await response.json()) as ExperimentApiPayload | ExperimentRow[];
        if (!isActive) {
          return;
        }
        const results = Array.isArray(payload) ? payload : (payload.results ?? []);
        const countValue =
          Array.isArray(payload) || typeof payload.count !== "number"
            ? results.length
            : payload.count;
        setExperiments(results);
        setTotalCount(countValue);
      } catch (_error) {
        if (!isActive) {
          return;
        }
        setExperiments([]);
        setTotalCount(0);
        setErrorMessage("We could not load experiment data. Please try again.");
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    void loadExperiments();

    return () => {
      isActive = false;
    };
  }, [buildExperimentsQueryParams, pageIndex, refreshToken]);

  const filterOptionLookup: Partial<Record<keyof ExperimentFilters, FilterOption[]>> = useMemo(
    () => ({
      basic_science_group: filterOptions?.basic_science_group ?? [],
      species: filterOptions?.species ?? [],
      sample_types: filterOptions?.sample_types ?? [],
      tissue_types: filterOptions?.tissue_types ?? [],
      is_deleted: filterOptions?.boolean ?? DEFAULT_BOOLEAN_OPTIONS,
    }),
    [filterOptions],
  );

  const exportParams = useMemo(() => {
    const params: Array<{ label: string; value: string }> = [];

    if (searchQuery.trim()) {
      params.push({ label: "Search", value: searchQuery.trim() });
    }

    if (includeDeleted) {
      params.push({ label: "Include deleted experiments", value: "Yes" });
    }

    Object.entries(filters).forEach(([key, value]) => {
      const trimmedValue = value.trim();
      if (!trimmedValue) {
        return;
      }
      const options = filterOptionLookup[key as keyof ExperimentFilters];
      const resolvedValue = options?.find((option) => option.value === trimmedValue)?.label;
      params.push({
        label: FILTER_LABELS[key as keyof ExperimentFilters] ?? key,
        value: resolvedValue ?? trimmedValue,
      });
    });

    if (orderingLabel) {
      params.push({ label: "Ordering", value: orderingLabel });
    }

    return params;
  }, [filters, includeDeleted, orderingLabel, searchQuery, filterOptionLookup]);

  const buildExportUrl = () => {
    const query = buildExperimentsQueryParams();
    const queryString = query.toString();
    return queryString
      ? `/api/dashboard/experiments/export?${queryString}`
      : "/api/dashboard/experiments/export";
  };

  const handleExportConfirm = () => {
    const url = buildExportUrl();
    window.open(url, "_blank", "noopener,noreferrer");
    setExportDialogOpen(false);
  };

  const hasExportConstraints = searchQuery.trim() !== "" || activeFilterCount > 0 || includeDeleted;

  const handleSortToggle = (key: SortKey) => {
    setSorting((previous) => {
      if (!previous || previous.id !== key) {
        return { id: key, desc: false };
      }
      if (!previous.desc) {
        return { id: key, desc: true };
      }
      return null;
    });
  };

  const getSortState = (key: SortKey) => {
    if (!sorting || sorting.id !== key) {
      return false;
    }
    return sorting.desc ? "desc" : "asc";
  };

  const handleExperimentCreated = () => {
    setPageIndex(1);
    setRefreshToken((previous) => previous + 1);
  };

  const handleExperimentUpdated = () => {
    setRefreshToken((previous) => previous + 1);
  };

  const handleEditClick = (experiment: ExperimentRow) => {
    setActiveExperiment(experiment);
    setEditDialogOpen(true);
  };

  const handleEditOpenChange = (open: boolean) => {
    setEditDialogOpen(open);
    if (!open) {
      setActiveExperiment(null);
    }
  };

  const closeDeleteDialog = (forceClose = false) => {
    if (isDeleting && !forceClose) {
      return;
    }
    setDeleteDialogOpen(false);
    setDeleteTarget(null);
    setDeleteError(null);
    setDeleteAction("delete");
  };

  const openDeleteDialog = (experiment: ExperimentRow, action: "delete" | "restore") => {
    setDeleteTarget(experiment);
    setDeleteAction(action);
    setDeleteError(null);
    setDeleteDialogOpen(true);
  };

  const handleDeleteDialogChange = (open: boolean) => {
    if (!open) {
      closeDeleteDialog();
      return;
    }
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deleteTarget) {
      return;
    }

    setIsDeleting(true);
    setDeleteError(null);

    try {
      const response =
        deleteAction === "restore"
          ? await fetch(`/api/dashboard/experiments/${deleteTarget.id}`, {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ is_deleted: false }),
            })
          : await fetch(`/api/dashboard/experiments/${deleteTarget.id}`, {
              method: "DELETE",
            });

      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        let errorDetail =
          deleteAction === "restore"
            ? "Unable to restore experiment."
            : "Unable to delete experiment.";
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
        setDeleteError(errorDetail);
        return;
      }

      setRefreshToken((previous) => previous + 1);
      closeDeleteDialog(true);
    } catch {
      setDeleteError("Something went wrong. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <ExperimentFormDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreated={handleExperimentCreated}
      />
      <ExperimentFormDialog
        open={editDialogOpen}
        onOpenChange={handleEditOpenChange}
        onUpdated={handleExperimentUpdated}
        mode="edit"
        experimentId={activeExperiment?.id ?? null}
        initialValues={
          activeExperiment
            ? {
                basic_science_group: activeExperiment.basic_science_group,
                name: activeExperiment.name,
                description: activeExperiment.description,
                date: activeExperiment.date,
                species: activeExperiment.species,
                sample_types: activeExperiment.sample_types,
                tissue_types: activeExperiment.tissue_types,
              }
            : undefined
        }
      />
      <Dialog open={deleteDialogOpen} onOpenChange={handleDeleteDialogChange}>
        <DialogContent showCloseButton={!isDeleting}>
          <DialogHeader>
            <DialogTitle>
              {deleteAction === "restore" ? "Restore experiment?" : "Delete experiment?"}
            </DialogTitle>
            <DialogDescription>
              {deleteAction === "restore"
                ? "This will restore the experiment to the active list."
                : "This will mark the experiment as deleted and remove it from the active list."}{" "}
              {deleteTarget?.name ?? "this experiment"}.
            </DialogDescription>
          </DialogHeader>
          {deleteError ? <p className="text-sm text-destructive">{deleteError}</p> : null}
          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => closeDeleteDialog()}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleConfirmDelete}
              disabled={isDeleting}
              variant={deleteAction === "restore" ? "default" : "destructive"}
            >
              {isDeleting ? "Updating..." : deleteAction === "restore" ? "Restore" : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Card>
        <CardHeader>
          <CardTitle>Experiments</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Button size="sm" onClick={() => setCreateDialogOpen(true)}>
              Add New Experiment
            </Button>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="Search by experiment ID or description"
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
                  checked={includeDeleted}
                  onChange={(event) => setIncludeDeleted(event.target.checked)}
                />
                Include deleted experiments?
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
                  htmlFor={`${filterSelectIdPrefix}-basic-science-group`}
                >
                  Basic science group
                  <Select
                    value={filters.basic_science_group || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        basic_science_group: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.basic_science_group,
                      )}
                      id={`${filterSelectIdPrefix}-basic-science-group`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.basic_science_group ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-species`}
                >
                  Species
                  <Select
                    value={filters.species || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        species: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.species,
                      )}
                      id={`${filterSelectIdPrefix}-species`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.species ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-sample-types`}
                >
                  Sample types
                  <Select
                    value={filters.sample_types || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        sample_types: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.sample_types,
                      )}
                      id={`${filterSelectIdPrefix}-sample-types`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.sample_types ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-tissue-types`}
                >
                  Tissue types
                  <Select
                    value={filters.tissue_types || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        tissue_types: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.tissue_types,
                      )}
                      id={`${filterSelectIdPrefix}-tissue-types`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.tissue_types ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-date-after`}
                >
                  Experiment date after
                  <Input
                    id={`${filterSelectIdPrefix}-date-after`}
                    type="date"
                    value={filters.date_after}
                    onChange={(event) =>
                      setFilters((previous) => ({
                        ...previous,
                        date_after: event.target.value,
                      }))
                    }
                    className={getFilterFieldClass("h-9", filters.date_after)}
                  />
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-date-before`}
                >
                  Experiment date before
                  <Input
                    id={`${filterSelectIdPrefix}-date-before`}
                    type="date"
                    value={filters.date_before}
                    onChange={(event) =>
                      setFilters((previous) => ({
                        ...previous,
                        date_before: event.target.value,
                      }))
                    }
                    className={getFilterFieldClass("h-9", filters.date_before)}
                  />
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-deleted`}
                >
                  Deleted experiments
                  <Select
                    value={filters.is_deleted || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        is_deleted: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.is_deleted,
                      )}
                      id={`${filterSelectIdPrefix}-deleted`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.boolean ?? DEFAULT_BOOLEAN_OPTIONS).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
              </div>
            </div>
          </div>
          {errorMessage ? (
            <AlertError>
              <AlertDescription>{errorMessage}</AlertDescription>
            </AlertError>
          ) : null}
          <TablePagination
            canPrevious={canPrevious}
            canNext={canNext}
            isLoading={isLoading}
            onPrevious={() => setPageIndex((previous) => Math.max(previous - 1, 1))}
            onNext={() => setPageIndex((previous) => previous + 1)}
            pageIndex={pageIndex}
            pageCount={pageCount}
            pageSize={DEFAULT_PAGE_SIZE}
            currentCount={experiments.length}
            totalCount={totalCount}
            itemLabel="experiments"
          />
          <Table className="[&_td]:px-3 [&_td]:py-2">
            <TableHeader>
              <TableRow>
                <TableHead className={TABLE_HEADER_CLASS}>
                  <SortableHeader
                    title="Name"
                    sortKey="name"
                    state={getSortState("name")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>
                  <SortableHeader
                    title="Date"
                    sortKey="date"
                    state={getSortState("date")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>
                  <SortableHeader
                    title="Group"
                    sortKey="basic_science_group"
                    state={getSortState("basic_science_group")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Description</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Sample Types</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Tissue Types</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Species</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Boxes</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>
                  <SortableHeader
                    title="Created"
                    sortKey="created"
                    state={getSortState("created")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Created By</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {experiments.length ? (
                experiments.map((experiment) => (
                  <TableRow
                    key={experiment.id}
                    className={experiment.is_deleted ? "bg-muted/50" : ""}
                  >
                    <TableCell>{experiment.name}</TableCell>
                    <TableCell>{formatDate(experiment.date)}</TableCell>
                    <TableCell>
                      {experiment.basic_science_group_label ||
                        experiment.basic_science_group ||
                        "N/A"}
                    </TableCell>
                    <TableCell>{experiment.description || "N/A"}</TableCell>
                    <TableCell>{formatList(experiment.sample_type_labels)}</TableCell>
                    <TableCell>{formatList(experiment.tissue_type_labels)}</TableCell>
                    <TableCell>{experiment.species_label || experiment.species || "N/A"}</TableCell>
                    <TableCell>
                      {experiment.boxes.length ? (
                        <div className="flex flex-col gap-1">
                          {experiment.boxes.map((box) => (
                            <Link
                              key={box.id}
                              href={`/boxes/${box.id}`}
                              className="text-primary underline"
                            >
                              {box.box_id}
                            </Link>
                          ))}
                        </div>
                      ) : (
                        "N/A"
                      )}
                    </TableCell>
                    <TableCell>{formatDate(experiment.created)}</TableCell>
                    <TableCell>{experiment.created_by_email || "N/A"}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button asChild variant="link" size="sm" className="h-auto p-0">
                          <Link href={`/experiments/${experiment.id}`}>
                            <Eye size={16} />
                            View
                          </Link>
                        </Button>
                        <Button
                          type="button"
                          variant="link"
                          size="sm"
                          className="h-auto p-0"
                          onClick={() => handleEditClick(experiment)}
                        >
                          <span className="inline-flex items-center gap-1">
                            <Edit size={16} />
                            Edit
                          </span>
                        </Button>
                        {experiment.is_deleted ? (
                          <Button
                            type="button"
                            variant="link"
                            size="sm"
                            className="h-auto p-0"
                            onClick={() => openDeleteDialog(experiment, "restore")}
                          >
                            <span className="inline-flex items-center gap-1">
                              <RotateCcw size={16} />
                              Restore
                            </span>
                          </Button>
                        ) : (
                          <Button
                            type="button"
                            variant="link"
                            size="sm"
                            className="h-auto p-0"
                            onClick={() => openDeleteDialog(experiment, "delete")}
                          >
                            <span className="inline-flex items-center gap-1">
                              <Trash2 size={16} />
                              Delete
                            </span>
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={11} className="text-center text-muted-foreground">
                    {isLoading ? "Loading experiments..." : "No experiments found."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          <TablePagination
            canPrevious={canPrevious}
            canNext={canNext}
            isLoading={isLoading}
            onPrevious={() => setPageIndex((previous) => Math.max(previous - 1, 1))}
            onNext={() => setPageIndex((previous) => previous + 1)}
            pageIndex={pageIndex}
            pageCount={pageCount}
            pageSize={DEFAULT_PAGE_SIZE}
            currentCount={experiments.length}
            totalCount={totalCount}
            itemLabel="experiments"
          />
        </CardContent>
        <CardFooter className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2"></div>
        </CardFooter>
      </Card>
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
              <span className="min-w-[160px] text-muted-foreground">Experiments to export</span>
              <span className="font-semibold text-foreground">{totalCount}</span>
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
    </div>
  );
}
