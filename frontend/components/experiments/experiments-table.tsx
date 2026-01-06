// frontend/components/experiments/experiments-table.tsx
// Renders the experiments dashboard table with search, export, and pagination controls.
// Exists to mirror the legacy Django experiment list in the Next.js dashboard.

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

const DEFAULT_PAGE_SIZE = 20;
const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

function formatDate(dateValue: string | null) {
  if (!dateValue) {
    return "N/A";
  }
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return "N/A";
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
  const [experiments, setExperiments] = useState<ExperimentRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const backendBaseUrl = getBackendBaseUrl();
  const canClear = Boolean(searchInput || searchQuery);

  const canPrevious = pageIndex > 1;
  const canNext = pageIndex * DEFAULT_PAGE_SIZE < totalCount;
  const displayStart = totalCount === 0 ? 0 : (pageIndex - 1) * DEFAULT_PAGE_SIZE + 1;
  const displayEnd = Math.min(pageIndex * DEFAULT_PAGE_SIZE, totalCount);

  const exportUrl = useMemo(() => {
    const params = new URLSearchParams();
    if (searchQuery) {
      params.set("query", searchQuery);
    }
    const query = params.toString();
    return query
      ? `/api/dashboard/experiments/export?${query}`
      : "/api/dashboard/experiments/export";
  }, [searchQuery]);

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
  }, [pageIndex, searchQuery]);

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Search Experiment IDs</CardTitle>
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
              placeholder="Search by experiment ID or description"
              className="h-9"
            />
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
                  setPageIndex(1);
                }}
              >
                Clear
              </Button>
              <Button asChild variant="outline" size="sm" className="ml-auto">
                <a href={`${backendBaseUrl}/boxes/experiments/filter/`}>Advanced Filtering</a>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Experiment IDs</CardTitle>
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
                <TableHead>Date</TableHead>
                <TableHead>Group</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Sample Types</TableHead>
                <TableHead>Tissue Types</TableHead>
                <TableHead>Species</TableHead>
                <TableHead>Boxes</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Created By</TableHead>
                <TableHead>View</TableHead>
                <TableHead>Edit</TableHead>
                <TableHead>Delete</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {experiments.length ? (
                experiments.map((experiment) => (
                  <TableRow key={experiment.id}>
                    <TableCell>{formatDate(experiment.date)}</TableCell>
                    <TableCell>
                      {experiment.basic_science_group_label ||
                        experiment.basic_science_group ||
                        "N/A"}
                    </TableCell>
                    <TableCell>{experiment.name}</TableCell>
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
                      <a
                        href={`${backendBaseUrl}/boxes/experiments/view/${experiment.id}/`}
                        className="text-primary underline"
                      >
                        View
                      </a>
                    </TableCell>
                    <TableCell>
                      <a
                        href={`${backendBaseUrl}/boxes/experiments/edit/${experiment.id}/`}
                        className="text-primary underline"
                      >
                        Edit
                      </a>
                    </TableCell>
                    <TableCell>
                      {experiment.is_deleted ? (
                        <a
                          href={`${backendBaseUrl}/boxes/experiments/restore/${experiment.id}/`}
                          className="text-primary underline"
                        >
                          Restore
                        </a>
                      ) : (
                        <a
                          href={`${backendBaseUrl}/boxes/experiments/delete/${experiment.id}/`}
                          className="text-primary underline"
                        >
                          Delete
                        </a>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={13} className="text-center text-muted-foreground">
                    {isLoading ? "Loading experiments..." : "No experiments found."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
        <CardFooter className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <Button asChild size="sm">
              <a href={`${backendBaseUrl}/boxes/experiments/create/`}>Add New Experiment</a>
            </Button>
            <Button
              asChild
              variant="outline"
              size="sm"
              title="Customize by searching for the experiments you want."
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
