// frontend/components/boxes/boxes-table.tsx
// Renders the boxes dashboard table with search, export, and pagination controls.
// Exists to mirror the legacy Django boxes list in the Next.js dashboard.

"use client";

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
import { getBackendBaseUrl } from "@/lib/auth";

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

const DEFAULT_PAGE_SIZE = 20;
const createdFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});
const experimentDateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "2-digit",
  year: "2-digit",
});

function formatExperimentDate(dateValue: string | null) {
  if (!dateValue) {
    return "";
  }
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return experimentDateFormatter.format(date);
}

function formatCreatedDate(dateValue: string | null) {
  if (!dateValue) {
    return "N/A";
  }
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return "N/A";
  }
  return createdFormatter.format(date);
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
  const [boxes, setBoxes] = useState<BoxRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const backendBaseUrl = getBackendBaseUrl();
  const canClear = Boolean(searchInput || searchQuery || includeUsed);

  const canPrevious = pageIndex > 1;
  const canNext = pageIndex * DEFAULT_PAGE_SIZE < totalCount;
  const displayStart = totalCount === 0 ? 0 : (pageIndex - 1) * DEFAULT_PAGE_SIZE + 1;
  const displayEnd = Math.min(pageIndex * DEFAULT_PAGE_SIZE, totalCount);

  const exportUrl = useMemo(() => {
    const params = new URLSearchParams();
    if (searchQuery) {
      params.set("query", searchQuery);
    }
    if (includeUsed) {
      params.set("include_used", "true");
    }
    const query = params.toString();
    return query ? `/api/dashboard/boxes/export?${query}` : "/api/dashboard/boxes/export";
  }, [includeUsed, searchQuery]);

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
  }, [includeUsed, pageIndex, searchQuery]);

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Search Boxes</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4"
            onSubmit={(event) => {
              event.preventDefault();
              setPageIndex(1);
              setSearchQuery(searchInput.trim());
            }}
          >
            <Input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search by box ID, location, experiment, or comments"
              className="h-9"
            />
            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-input text-primary"
                checked={includeUsed}
                onChange={(event) => {
                  setIncludeUsed(event.target.checked);
                  setPageIndex(1);
                }}
              />
              Include used boxes?
            </label>
            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" size="sm" disabled={isLoading}>
                Search
              </Button>
              <Button
                type="button"
                size="sm"
                variant="secondary"
                disabled={!canClear || isLoading}
                onClick={() => {
                  setSearchInput("");
                  setSearchQuery("");
                  setIncludeUsed(false);
                  setPageIndex(1);
                }}
              >
                Clear
              </Button>
              <Button asChild variant="outline" size="sm" className="ml-auto">
                <a href={`${backendBaseUrl}/boxes/filter/`}>Advanced Filtering</a>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Basic Science Boxes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-muted-foreground">
            <span>Total Count: {totalCount}</span>
            {totalCount > 0 ? (
              <span>
                Showing {displayStart}-{displayEnd} of {totalCount}
              </span>
            ) : null}
          </div>
          {errorMessage ? (
            <AlertError>
              <AlertDescription>{errorMessage}</AlertDescription>
            </AlertError>
          ) : null}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Box ID</TableHead>
                <TableHead>Groups</TableHead>
                <TableHead>Experiment IDs</TableHead>
                <TableHead>Species</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Sublocation</TableHead>
                <TableHead>Box Type</TableHead>
                <TableHead>Sample Types</TableHead>
                <TableHead>Tissue Types</TableHead>
                <TableHead>Comments</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Created By</TableHead>
                <TableHead>View</TableHead>
                <TableHead>Edit</TableHead>
                <TableHead>Delete</TableHead>
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
                      <TableCell>{box.box_id}</TableCell>
                      <TableCell>{box.basic_science_groups_display || "N/A"}</TableCell>
                      <TableCell>{experimentsLabel}</TableCell>
                      <TableCell>{box.species_display || "N/A"}</TableCell>
                      <TableCell>{box.location_label || box.location || "N/A"}</TableCell>
                      <TableCell>{sublocation}</TableCell>
                      <TableCell>{box.box_type_label || box.box_type || "N/A"}</TableCell>
                      <TableCell>{formatList(box.sample_type_labels)}</TableCell>
                      <TableCell>{formatList(box.tissue_type_labels)}</TableCell>
                      <TableCell>{box.comments || "N/A"}</TableCell>
                      <TableCell>{formatCreatedDate(box.created)}</TableCell>
                      <TableCell>{box.created_by_email || "N/A"}</TableCell>
                      <TableCell>
                        <Link href={`/boxes/${box.id}`} className="text-primary underline">
                          View
                        </Link>
                      </TableCell>
                      <TableCell>
                        <a
                          href={`${backendBaseUrl}/boxes/edit/${box.id}/`}
                          className="text-primary underline"
                        >
                          Edit
                        </a>
                      </TableCell>
                      <TableCell>
                        <a
                          href={`${backendBaseUrl}/boxes/delete/${box.id}/`}
                          className="text-primary underline"
                        >
                          Used
                        </a>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={15} className="text-center text-muted-foreground">
                    {isLoading ? "Loading boxes..." : "No boxes found."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
        <CardFooter className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <Button asChild size="sm">
              <a href={`${backendBaseUrl}/boxes/create/`}>Add New Box</a>
            </Button>
            <Button
              asChild
              variant="outline"
              size="sm"
              title="Customize by searching for the boxes you want."
            >
              <a href={exportUrl}>Export Current View to CSV</a>
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={!canPrevious || isLoading}
              onClick={() => setPageIndex((previous) => Math.max(previous - 1, 1))}
            >
              Previous
            </Button>
            <span className="text-xs text-muted-foreground">
              Page {pageIndex}
              {totalCount > 0 ? ` of ${Math.ceil(totalCount / DEFAULT_PAGE_SIZE)}` : null}
            </span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={!canNext || isLoading}
              onClick={() => setPageIndex((previous) => previous + 1)}
            >
              Next
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
