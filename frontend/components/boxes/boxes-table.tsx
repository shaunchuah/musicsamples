// frontend/components/boxes/boxes-table.tsx
// Renders the boxes dashboard table with search, export, and pagination controls.
// Exists to mirror the legacy Django boxes list in the Next.js dashboard.

"use client";

import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Download,
  Edit,
  Eye,
  Filter,
  Trash2,
  X,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useId, useMemo, useState } from "react";

import { BoxFormDialog } from "@/components/boxes/box-form-dialog";
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

type BoxExperimentSummary = {
  id: number;
  name: string;
  date: string | null;
};

type BoxRow = {
  id: number;
  box_id: string;
  basic_science_group: string;
  basic_science_group_label: string | null;
  basic_science_groups_display: string | null;
  experiments: BoxExperimentSummary[];
  species_display: string | null;
  location: string;
  location_label: string | null;
  row: string | null;
  column: string | null;
  depth: string | null;
  sublocation: string | null;
  box_type: string;
  box_type_label: string | null;
  sample_type_labels: string[];
  tissue_type_labels: string[];
  comments: string | null;
  created: string | null;
  created_by_email: string | null;
  is_used: boolean;
};

type BoxApiPayload = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: BoxRow[];
};

type FilterOption = {
  value: string;
  label: string;
};

type BoxFilterOptions = {
  basic_science_group: FilterOption[];
  box_type: FilterOption[];
  location: FilterOption[];
  row: FilterOption[];
  column: FilterOption[];
  depth: FilterOption[];
  experiments: FilterOption[];
  sample_types: FilterOption[];
  tissue_types: FilterOption[];
  boolean: FilterOption[];
};

type BoxFilters = {
  basic_science_group: string;
  box_type: string;
  location: string;
  row: string;
  column: string;
  depth: string;
  experiments: string;
  experiments_date_after: string;
  experiments_date_before: string;
  sample_types: string;
  tissue_types: string;
  is_used: string;
};

type SortKey = "box_id" | "location" | "box_type" | "created";

const DEFAULT_PAGE_SIZE = 20;
const EMPTY_SELECT_VALUE = "__none__";
const DEFAULT_FILTERS: BoxFilters = {
  basic_science_group: "",
  box_type: "",
  location: "",
  row: "",
  column: "",
  depth: "",
  experiments: "",
  experiments_date_after: "",
  experiments_date_before: "",
  sample_types: "",
  tissue_types: "",
  is_used: "",
};
const DEFAULT_BOOLEAN_OPTIONS: FilterOption[] = [
  { value: "true", label: "Yes" },
  { value: "false", label: "No" },
];

const SORT_FIELD_MAP: Record<SortKey, string> = {
  box_id: "box_id",
  location: "location",
  box_type: "box_type",
  created: "created",
};

const SORT_LABELS: Record<SortKey, string> = {
  box_id: "Box ID",
  location: "Location",
  box_type: "Box type",
  created: "Created",
};

type SortState = {
  id: SortKey;
  desc: boolean;
} | null;

const TABLE_HEADER_CLASS =
  "px-3 py-2 text-sm font-semibold normal-case tracking-normal text-muted-foreground";

const FILTER_LABELS: Record<keyof BoxFilters, string> = {
  basic_science_group: "Basic science group",
  box_type: "Box type",
  location: "Location",
  row: "Row",
  column: "Column",
  depth: "Depth",
  experiments: "Experiment",
  experiments_date_after: "Experiment date after",
  experiments_date_before: "Experiment date before",
  sample_types: "Sample types",
  tissue_types: "Tissue types",
  is_used: "Used boxes",
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

function formatExperimentDate(dateValue: string | null) {
  if (!dateValue) {
    return "";
  }
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return dateFormatter.format(date);
}

function formatCreatedDate(dateValue: string | null) {
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
    return "-";
  }
  return values.join(", ");
}

export function BoxesTable() {
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [includeUsed, setIncludeUsed] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filterOptions, setFilterOptions] = useState<BoxFilterOptions | null>(null);
  const [filters, setFilters] = useState<BoxFilters>(DEFAULT_FILTERS);
  const [pageIndex, setPageIndex] = useState(1);
  const [sorting, setSorting] = useState<SortState>(null);
  const [boxes, setBoxes] = useState<BoxRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [activeBox, setActiveBox] = useState<BoxRow | null>(null);
  const [usedDialogOpen, setUsedDialogOpen] = useState(false);
  const [usedTarget, setUsedTarget] = useState<BoxRow | null>(null);
  const [isMarkingUsed, setIsMarkingUsed] = useState(false);
  const [usedError, setUsedError] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const experimentAfterInputId = useId();
  const experimentBeforeInputId = useId();
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

  const buildBoxesQueryParams = useCallback(() => {
    const params = new URLSearchParams();
    if (searchQuery) {
      params.set("query", searchQuery);
    }
    if (includeUsed) {
      params.set("include_used", "true");
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
  }, [filters, includeUsed, orderingValue, searchQuery]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setPageIndex((previous) => (previous === 1 ? previous : 1));
  }, [includeUsed, searchQuery, sorting, filters]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadFilterOptions() {
      try {
        const response = await fetch("/api/dashboard/boxes/filters", {
          signal: controller.signal,
        });

        if (!response.ok) {
          return;
        }

        const payload = (await response.json()) as BoxFilterOptions;
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

    const loadBoxes = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const params = buildBoxesQueryParams();
        params.set("page", String(pageIndex));
        params.set("page_size", String(DEFAULT_PAGE_SIZE));

        const response = await fetch(`/api/dashboard/boxes/search?${params.toString()}`, {
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error("Unable to load boxes.");
        }
        const payload = (await response.json()) as BoxApiPayload | BoxRow[];
        if (!isActive) {
          return;
        }
        const results = Array.isArray(payload) ? payload : (payload.results ?? []);
        const countValue =
          Array.isArray(payload) || typeof payload.count !== "number"
            ? results.length
            : payload.count;
        setBoxes(results);
        setTotalCount(countValue);
      } catch (_error) {
        if (!isActive) {
          return;
        }
        setBoxes([]);
        setTotalCount(0);
        setErrorMessage("We could not load box data. Please try again.");
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    void loadBoxes();

    return () => {
      isActive = false;
    };
  }, [buildBoxesQueryParams, pageIndex, refreshToken]);

  const filterOptionLookup: Partial<Record<keyof BoxFilters, FilterOption[]>> = useMemo(
    () => ({
      basic_science_group: filterOptions?.basic_science_group ?? [],
      box_type: filterOptions?.box_type ?? [],
      location: filterOptions?.location ?? [],
      row: filterOptions?.row ?? [],
      column: filterOptions?.column ?? [],
      depth: filterOptions?.depth ?? [],
      experiments: filterOptions?.experiments ?? [],
      sample_types: filterOptions?.sample_types ?? [],
      tissue_types: filterOptions?.tissue_types ?? [],
      is_used: filterOptions?.boolean ?? DEFAULT_BOOLEAN_OPTIONS,
    }),
    [filterOptions],
  );

  const exportParams = useMemo(() => {
    const params: Array<{ label: string; value: string }> = [];

    if (searchQuery.trim()) {
      params.push({ label: "Search", value: searchQuery.trim() });
    }

    if (includeUsed) {
      params.push({ label: "Include used boxes", value: "Yes" });
    }

    Object.entries(filters).forEach(([key, value]) => {
      const trimmedValue = value.trim();
      if (!trimmedValue) {
        return;
      }
      const options = filterOptionLookup[key as keyof BoxFilters];
      const resolvedValue = options?.find((option) => option.value === trimmedValue)?.label;
      params.push({
        label: FILTER_LABELS[key as keyof BoxFilters] ?? key,
        value: resolvedValue ?? trimmedValue,
      });
    });

    if (orderingLabel) {
      params.push({ label: "Ordering", value: orderingLabel });
    }

    return params;
  }, [filters, includeUsed, orderingLabel, searchQuery, filterOptionLookup]);

  const buildExportUrl = () => {
    const query = buildBoxesQueryParams();
    const queryString = query.toString();
    return queryString
      ? `/api/dashboard/boxes/export?${queryString}`
      : "/api/dashboard/boxes/export";
  };

  const handleExportConfirm = () => {
    const url = buildExportUrl();
    window.open(url, "_blank", "noopener,noreferrer");
    setExportDialogOpen(false);
  };

  const hasExportConstraints = searchQuery.trim() !== "" || activeFilterCount > 0 || includeUsed;

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

  const handleBoxCreated = () => {
    setPageIndex(1);
    setRefreshToken((previous) => previous + 1);
  };

  const handleBoxUpdated = () => {
    setRefreshToken((previous) => previous + 1);
  };

  const handleEditClick = (box: BoxRow) => {
    setActiveBox(box);
    setEditDialogOpen(true);
  };

  const handleEditOpenChange = (open: boolean) => {
    setEditDialogOpen(open);
    if (!open) {
      setActiveBox(null);
    }
  };

  const closeUsedDialog = (forceClose = false) => {
    if (isMarkingUsed && !forceClose) {
      return;
    }
    setUsedDialogOpen(false);
    setUsedTarget(null);
    setUsedError(null);
  };

  const openUsedDialog = (box: BoxRow) => {
    setUsedTarget(box);
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
      const response = await fetch(`/api/dashboard/boxes/${usedTarget.id}`, {
        method: "DELETE",
      });

      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        let errorDetail = "Unable to mark box as used.";
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

      setRefreshToken((previous) => previous + 1);
      closeUsedDialog(true);
    } catch {
      setUsedError("Something went wrong. Please try again.");
    } finally {
      setIsMarkingUsed(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <BoxFormDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreated={handleBoxCreated}
      />
      <BoxFormDialog
        open={editDialogOpen}
        onOpenChange={handleEditOpenChange}
        onUpdated={handleBoxUpdated}
        mode="edit"
        boxId={activeBox?.id ?? null}
        initialValues={
          activeBox
            ? {
                box_id: activeBox.box_id,
                basic_science_group: activeBox.basic_science_group,
                box_type: activeBox.box_type,
                location: activeBox.location,
                row: activeBox.row,
                column: activeBox.column,
                depth: activeBox.depth,
                comments: activeBox.comments,
                experiments: activeBox.experiments.map((experiment) => experiment.id),
              }
            : undefined
        }
      />
      <Dialog open={usedDialogOpen} onOpenChange={handleUsedDialogChange}>
        <DialogContent showCloseButton={!isMarkingUsed}>
          <DialogHeader>
            <DialogTitle>Mark box as used?</DialogTitle>
            <DialogDescription>
              This will mark box {usedTarget?.box_id ?? "this box"} as used and remove it from the
              active list.
            </DialogDescription>
          </DialogHeader>
          {usedError ? <p className="text-sm text-destructive">{usedError}</p> : null}
          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => closeUsedDialog()}
              disabled={isMarkingUsed}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleConfirmUsed}
              disabled={isMarkingUsed}
              variant="destructive"
            >
              {isMarkingUsed ? "Marking..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Card>
        <CardHeader>
          <CardTitle>Basic Science Boxes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Button size="sm" onClick={() => setCreateDialogOpen(true)}>
              Add New Box
            </Button>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="Search by box ID, location, experiment, or comments"
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
                Include used boxes?
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
                  htmlFor={`${filterSelectIdPrefix}-box-type`}
                >
                  Box type
                  <Select
                    value={filters.box_type || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        box_type: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.box_type,
                      )}
                      id={`${filterSelectIdPrefix}-box-type`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.box_type ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-location`}
                >
                  Location
                  <Select
                    value={filters.location || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        location: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.location,
                      )}
                      id={`${filterSelectIdPrefix}-location`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.location ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-row`}
                >
                  Row
                  <Select
                    value={filters.row || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        row: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.row,
                      )}
                      id={`${filterSelectIdPrefix}-row`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.row ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-column`}
                >
                  Column
                  <Select
                    value={filters.column || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        column: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.column,
                      )}
                      id={`${filterSelectIdPrefix}-column`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.column ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-depth`}
                >
                  Depth
                  <Select
                    value={filters.depth || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        depth: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.depth,
                      )}
                      id={`${filterSelectIdPrefix}-depth`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.depth ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={`${filterSelectIdPrefix}-experiments`}
                >
                  Experiment
                  <Select
                    value={filters.experiments || EMPTY_SELECT_VALUE}
                    onValueChange={(value) =>
                      setFilters((previous) => ({
                        ...previous,
                        experiments: value === EMPTY_SELECT_VALUE ? "" : value,
                      }))
                    }
                  >
                    <SelectTrigger
                      className={getFilterFieldClass(
                        "h-9 w-full text-sm text-foreground",
                        filters.experiments,
                      )}
                      id={`${filterSelectIdPrefix}-experiments`}
                    >
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={EMPTY_SELECT_VALUE}>Any</SelectItem>
                      {(filterOptions?.experiments ?? []).map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={experimentAfterInputId}
                >
                  Experiment date after
                  <Input
                    id={experimentAfterInputId}
                    type="date"
                    value={filters.experiments_date_after}
                    onChange={(event) =>
                      setFilters((previous) => ({
                        ...previous,
                        experiments_date_after: event.target.value,
                      }))
                    }
                    className={getFilterFieldClass("h-9", filters.experiments_date_after)}
                  />
                </label>
                <label
                  className="flex flex-col gap-1 text-xs text-muted-foreground"
                  htmlFor={experimentBeforeInputId}
                >
                  Experiment date before
                  <Input
                    id={experimentBeforeInputId}
                    type="date"
                    value={filters.experiments_date_before}
                    onChange={(event) =>
                      setFilters((previous) => ({
                        ...previous,
                        experiments_date_before: event.target.value,
                      }))
                    }
                    className={getFilterFieldClass("h-9", filters.experiments_date_before)}
                  />
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
                  htmlFor={`${filterSelectIdPrefix}-used-boxes`}
                >
                  Used boxes
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
                      id={`${filterSelectIdPrefix}-used-boxes`}
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
            currentCount={boxes.length}
            totalCount={totalCount}
            itemLabel="boxes"
          />
          <Table className="[&_td]:px-3 [&_td]:py-2">
            <TableHeader>
              <TableRow>
                <TableHead className={TABLE_HEADER_CLASS}>
                  <SortableHeader
                    title="Box ID"
                    sortKey="box_id"
                    state={getSortState("box_id")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Group</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>
                  <SortableHeader
                    title="Location"
                    sortKey="location"
                    state={getSortState("location")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Sublocation</TableHead>
                <TableHead className={`${TABLE_HEADER_CLASS} whitespace-nowrap`}>
                  <SortableHeader
                    title="Box Type"
                    sortKey="box_type"
                    state={getSortState("box_type")}
                    onToggle={handleSortToggle}
                  />
                </TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Experiments</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Species</TableHead>

                <TableHead className={TABLE_HEADER_CLASS}>Sample Types</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Tissue Types</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Comments</TableHead>
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
              {boxes.length ? (
                boxes.map((box) => {
                  const experimentsLabel = box.experiments.length
                    ? box.experiments
                        .map((experiment) => {
                          const dateLabel = formatExperimentDate(experiment.date);
                          return dateLabel ? `${experiment.name} ${dateLabel}` : experiment.name;
                        })
                        .join(", ")
                    : "-";
                  const sublocation =
                    box.sublocation ??
                    (`${box.row ?? ""}${box.column ?? ""}${box.depth ?? ""}`.trim() || "-");

                  return (
                    <TableRow key={box.id}>
                      <TableCell className="whitespace-nowrap">{box.box_id}</TableCell>
                      <TableCell>
                        {box.basic_science_group_label || box.basic_science_group || "-"}
                      </TableCell>
                      <TableCell className="whitespace-nowrap">
                        {box.location_label || box.location || "-"}
                      </TableCell>
                      <TableCell>{sublocation}</TableCell>
                      <TableCell>{box.box_type_label || box.box_type || "-"}</TableCell>
                      <TableCell>{experimentsLabel}</TableCell>
                      <TableCell>{box.species_display || "-"}</TableCell>

                      <TableCell>{formatList(box.sample_type_labels)}</TableCell>
                      <TableCell>{formatList(box.tissue_type_labels)}</TableCell>
                      <TableCell>{box.comments || "-"}</TableCell>
                      <TableCell>{formatCreatedDate(box.created)}</TableCell>
                      <TableCell>{box.created_by_email || "-"}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button asChild variant="link" size="sm" className="h-auto p-0">
                            <Link href={`/boxes/${box.id}`}>
                              <Eye size={16} />
                              View
                            </Link>
                          </Button>
                          <Button
                            type="button"
                            variant="link"
                            size="sm"
                            className="h-auto p-0"
                            onClick={() => handleEditClick(box)}
                          >
                            <span className="inline-flex items-center gap-1">
                              <Edit size={16} />
                              Edit
                            </span>
                          </Button>
                          <Button
                            type="button"
                            variant="link"
                            size="sm"
                            className="h-auto p-0"
                            onClick={() => openUsedDialog(box)}
                          >
                            <span className="inline-flex items-center gap-1">
                              <Trash2 size={16} />
                              Used
                            </span>
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={13} className="text-center text-muted-foreground">
                    {isLoading ? "Loading boxes..." : "No boxes found."}
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
            currentCount={boxes.length}
            totalCount={totalCount}
            itemLabel="boxes"
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
              <span className="min-w-[160px] text-muted-foreground">Boxes to export</span>
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
