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
import { useEffect, useMemo, useState } from "react";

import { AlertDescription, AlertError } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TablePagination } from "@/components/ui/table-pagination";
import { getBackendBaseUrl } from "@/lib/auth";
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
  sample_type_labels: string[];
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

const SORT_FIELD_MAP: Record<SortKey, string> = {
  date: "date",
  basic_science_group: "basic_science_group",
  name: "name",
  created: "created",
};

type SortState = {
  id: SortKey;
  desc: boolean;
} | null;

const TABLE_HEADER_CLASS =
  "px-3 py-2 text-sm font-semibold normal-case tracking-normal text-muted-foreground";

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
  const [pageIndex, setPageIndex] = useState(1);
  const [sorting, setSorting] = useState<SortState>({ id: "date", desc: true });
  const [experiments, setExperiments] = useState<ExperimentRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const backendBaseUrl = getBackendBaseUrl();

  const canPrevious = pageIndex > 1;
  const canNext = pageIndex * DEFAULT_PAGE_SIZE < totalCount;
  const pageCount = totalCount > 0 ? Math.ceil(totalCount / DEFAULT_PAGE_SIZE) : 0;

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

  const exportUrl = useMemo(() => {
    const params = new URLSearchParams();
    if (searchQuery) {
      params.set("query", searchQuery);
    }
    if (orderingValue) {
      params.set("ordering", orderingValue);
    }
    const query = params.toString();
    return query
      ? `/api/dashboard/experiments/export?${query}`
      : "/api/dashboard/experiments/export";
  }, [orderingValue, searchQuery]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setPageIndex((previous) => (previous === 1 ? previous : 1));
  }, [searchQuery, sorting]);

  useEffect(() => {
    let isActive = true;

    const loadExperiments = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const params = new URLSearchParams();
        if (searchQuery) {
          params.set("query", searchQuery);
        }
        if (orderingValue) {
          params.set("ordering", orderingValue);
        }
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
  }, [orderingValue, pageIndex, searchQuery]);

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

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Experiments</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Button asChild size="sm">
              <a href={`${backendBaseUrl}/boxes/experiments/create/`}>Add New Experiment</a>
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
            </div>
            <div className="flex items-center gap-2">
              <Button asChild variant="outline" size="sm">
                <a href={`${backendBaseUrl}/boxes/experiments/filter/`}>
                  <Filter className="mr-2 h-4 w-4" />
                  Filters
                </a>
              </Button>
              <Button asChild variant="outline" size="sm">
                <a href={exportUrl}>
                  <Download className="mr-2 h-4 w-4" />
                  Export CSV
                </a>
              </Button>
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
                          <a href={`${backendBaseUrl}/boxes/experiments/view/${experiment.id}/`}>
                            <Eye size={16} />
                            View
                          </a>
                        </Button>
                        <Button asChild variant="link" size="sm" className="h-auto p-0">
                          <a href={`${backendBaseUrl}/boxes/experiments/edit/${experiment.id}/`}>
                            <Edit size={16} />
                            Edit
                          </a>
                        </Button>
                        {experiment.is_deleted ? (
                          <Button asChild variant="link" size="sm" className="h-auto p-0">
                            <a
                              href={`${backendBaseUrl}/boxes/experiments/restore/${experiment.id}/`}
                            >
                              <RotateCcw size={16} />
                              Restore
                            </a>
                          </Button>
                        ) : (
                          <Button asChild variant="link" size="sm" className="h-auto p-0">
                            <a
                              href={`${backendBaseUrl}/boxes/experiments/delete/${experiment.id}/`}
                            >
                              <Trash2 size={16} />
                              Delete
                            </a>
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
    </div>
  );
}
