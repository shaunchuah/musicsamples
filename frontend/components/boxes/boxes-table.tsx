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
import { useEffect, useMemo, useState } from "react";

import { BoxFormDialog } from "@/components/boxes/box-form-dialog";
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

type BoxExperimentSummary = {
  id: number;
  name: string;
  date: string | null;
};

type BoxRow = {
  id: number;
  box_id: string;
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

type SortKey = "box_id" | "location" | "box_type" | "created";

const DEFAULT_PAGE_SIZE = 20;

const SORT_FIELD_MAP: Record<SortKey, string> = {
  box_id: "box_id",
  location: "location",
  box_type: "box_type",
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
    return "N/A";
  }
  return values.join(", ");
}

export function BoxesTable() {
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [includeUsed, setIncludeUsed] = useState(false);
  const [pageIndex, setPageIndex] = useState(1);
  const [sorting, setSorting] = useState<SortState>(null);
  const [boxes, setBoxes] = useState<BoxRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);
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
    if (includeUsed) {
      params.set("include_used", "true");
    }
    if (orderingValue) {
      params.set("ordering", orderingValue);
    }
    const query = params.toString();
    return query ? `/api/dashboard/boxes/export?${query}` : "/api/dashboard/boxes/export";
  }, [includeUsed, orderingValue, searchQuery]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setPageIndex((previous) => (previous === 1 ? previous : 1));
  }, [includeUsed, searchQuery, sorting]);

  useEffect(() => {
    let isActive = true;

    const loadBoxes = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
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
  }, [includeUsed, orderingValue, pageIndex, refreshToken, searchQuery]);

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

  return (
    <div className="flex flex-col gap-6">
      <BoxFormDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreated={handleBoxCreated}
      />
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
              <Button asChild variant="outline" size="sm">
                <a href={`${backendBaseUrl}/boxes/filter/`}>
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
                <TableHead className={TABLE_HEADER_CLASS}>Groups</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Experiment IDs</TableHead>
                <TableHead className={TABLE_HEADER_CLASS}>Species</TableHead>
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
                    : "N/A";
                  const sublocation =
                    box.sublocation ??
                    (`${box.row ?? ""}${box.column ?? ""}${box.depth ?? ""}`.trim() || "N/A");

                  return (
                    <TableRow key={box.id}>
                      <TableCell className="whitespace-nowrap">{box.box_id}</TableCell>
                      <TableCell>{box.basic_science_groups_display || "N/A"}</TableCell>
                      <TableCell>{experimentsLabel}</TableCell>
                      <TableCell>{box.species_display || "N/A"}</TableCell>
                      <TableCell className="whitespace-nowrap">
                        {box.location_label || box.location || "N/A"}
                      </TableCell>
                      <TableCell>{sublocation}</TableCell>
                      <TableCell>{box.box_type_label || box.box_type || "N/A"}</TableCell>
                      <TableCell>{formatList(box.sample_type_labels)}</TableCell>
                      <TableCell>{formatList(box.tissue_type_labels)}</TableCell>
                      <TableCell>{box.comments || "N/A"}</TableCell>
                      <TableCell>{formatCreatedDate(box.created)}</TableCell>
                      <TableCell>{box.created_by_email || "N/A"}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button asChild variant="link" size="sm" className="h-auto p-0">
                            <Link href={`/boxes/${box.id}`}>
                              <Eye size={16} />
                              View
                            </Link>
                          </Button>
                          <Button asChild variant="link" size="sm" className="h-auto p-0">
                            <a href={`${backendBaseUrl}/boxes/edit/${box.id}/`}>
                              <Edit size={16} />
                              Edit
                            </a>
                          </Button>
                          <Button asChild variant="link" size="sm" className="h-auto p-0">
                            <a href={`${backendBaseUrl}/boxes/delete/${box.id}/`}>
                              <Trash2 size={16} />
                              Used
                            </a>
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
    </div>
  );
}
