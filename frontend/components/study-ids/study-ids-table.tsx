// frontend/components/study-ids/study-ids-table.tsx
// Renders the study ID dashboard table with search, pagination, and row actions.
// Exists to mirror the legacy study ID list in the Next.js frontend while using v3 APIs.

"use client";

import { ChevronDown, Edit, Eye, Trash2, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useDashboardUser } from "@/components/dashboard/user-profile-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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

type StudyIdSampleSummary = {
  id: number;
  sample_id: string;
  sample_type_label: string | null;
};

type StudyIdFileSummary = {
  id: number;
  file_name: string | null;
};

type StudyIdRow = {
  id: number;
  name: string;
  study_name: string | null;
  study_name_label: string | null;
  study_group: string | null;
  study_group_label: string | null;
  age: number | null;
  sex: string | null;
  sex_label: string | null;
  study_center: string | null;
  study_center_label: string | null;
  genotype_data_available: boolean | null;
  nod2_mutation_present: boolean | null;
  il23r_mutation_present: boolean | null;
  sample_count: number;
  file_count: number;
};

type StudyIdApiPayload = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: StudyIdRow[];
};

type LazyLoadState<T> = {
  items: T[];
  isLoading: boolean;
  error: string | null;
  loaded: boolean;
};

const DEFAULT_PAGE_SIZE = 20;

const formatBoolean = (value: boolean | null | undefined) => {
  if (value === true) {
    return "Yes";
  }
  if (value === false) {
    return "No";
  }
  return "-";
};

const formatText = (value: string | null | undefined) => {
  if (!value) {
    return "-";
  }
  return value;
};

export function StudyIdsTable() {
  const { user } = useDashboardUser();
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [pageIndex, setPageIndex] = useState(1);
  const [rows, setRows] = useState<StudyIdRow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<StudyIdRow | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);
  const [samplesById, setSamplesById] = useState<
    Record<number, LazyLoadState<StudyIdSampleSummary>>
  >({});
  const [filesById, setFilesById] = useState<Record<number, LazyLoadState<StudyIdFileSummary>>>({});

  const isStaff = Boolean(user?.isStaff || user?.isSuperuser);

  const canPrevious = pageIndex > 1;
  const canNext = pageIndex * DEFAULT_PAGE_SIZE < totalCount;
  const pageCount = totalCount > 0 ? Math.ceil(totalCount / DEFAULT_PAGE_SIZE) : 0;

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setPageIndex(1);
  }, [searchQuery]);

  useEffect(() => {
    let isActive = true;

    const loadStudyIds = async () => {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const params = new URLSearchParams();
        if (searchQuery) {
          params.set("query", searchQuery);
        }
        params.set("page", String(pageIndex));
        params.set("page_size", String(DEFAULT_PAGE_SIZE));

        const response = await fetch(`/api/dashboard/study-ids/search?${params.toString()}`, {
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error("Unable to load study IDs.");
        }

        const payload = (await response.json()) as StudyIdApiPayload | StudyIdRow[];
        if (!isActive) {
          return;
        }

        const results = Array.isArray(payload) ? payload : (payload.results ?? []);
        const countValue =
          Array.isArray(payload) || typeof payload.count !== "number"
            ? results.length
            : payload.count;
        setRows(results);
        setTotalCount(countValue);
      } catch (error) {
        if (!isActive) {
          return;
        }
        setRows([]);
        setTotalCount(0);
        setErrorMessage(error instanceof Error ? error.message : "We could not load study IDs.");
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    void loadStudyIds();

    return () => {
      isActive = false;
    };
  }, [pageIndex, refreshToken, searchQuery]);

  const openDeleteDialog = (studyId: StudyIdRow) => {
    setDeleteTarget(studyId);
    setDeleteError(null);
    setDeleteDialogOpen(true);
  };

  const closeDeleteDialog = () => {
    if (isDeleting) {
      return;
    }
    setDeleteDialogOpen(false);
    setDeleteTarget(null);
    setDeleteError(null);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) {
      return;
    }
    setIsDeleting(true);
    setDeleteError(null);

    try {
      const response = await fetch(`/api/dashboard/study-ids/${deleteTarget.id}`, {
        method: "DELETE",
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(payload?.detail ?? "Unable to delete study ID.");
      }

      setDeleteDialogOpen(false);
      setDeleteTarget(null);
      setRefreshToken((previous) => previous + 1);
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : "Unable to delete study ID.");
    } finally {
      setIsDeleting(false);
    }
  };

  const loadSamples = async (row: StudyIdRow) => {
    if (row.sample_count <= 0) {
      return;
    }
    const existing = samplesById[row.id];
    if (existing?.isLoading || existing?.loaded) {
      return;
    }

    setSamplesById((previous) => ({
      ...previous,
      [row.id]: {
        items: existing?.items ?? [],
        isLoading: true,
        error: null,
        loaded: false,
      },
    }));

    try {
      const response = await fetch(`/api/dashboard/study-ids/${row.id}/samples`, {
        cache: "no-store",
      });
      const payload = (await response.json().catch(() => null)) as StudyIdSampleSummary[] | null;
      if (!response.ok) {
        throw new Error("Unable to load samples.");
      }
      setSamplesById((previous) => ({
        ...previous,
        [row.id]: {
          items: Array.isArray(payload) ? payload : [],
          isLoading: false,
          error: null,
          loaded: true,
        },
      }));
    } catch (error) {
      setSamplesById((previous) => ({
        ...previous,
        [row.id]: {
          items: [],
          isLoading: false,
          error: error instanceof Error ? error.message : "Unable to load samples.",
          loaded: false,
        },
      }));
    }
  };

  const loadFiles = async (row: StudyIdRow) => {
    if (row.file_count <= 0) {
      return;
    }
    const existing = filesById[row.id];
    if (existing?.isLoading || existing?.loaded) {
      return;
    }

    setFilesById((previous) => ({
      ...previous,
      [row.id]: {
        items: existing?.items ?? [],
        isLoading: true,
        error: null,
        loaded: false,
      },
    }));

    try {
      const response = await fetch(`/api/dashboard/study-ids/${row.id}/files`, {
        cache: "no-store",
      });
      const payload = (await response.json().catch(() => null)) as StudyIdFileSummary[] | null;
      if (!response.ok) {
        throw new Error("Unable to load files.");
      }
      setFilesById((previous) => ({
        ...previous,
        [row.id]: {
          items: Array.isArray(payload) ? payload : [],
          isLoading: false,
          error: null,
          loaded: true,
        },
      }));
    } catch (error) {
      setFilesById((previous) => ({
        ...previous,
        [row.id]: {
          items: [],
          isLoading: false,
          error: error instanceof Error ? error.message : "Unable to load files.",
          loaded: false,
        },
      }));
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Study IDs</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="relative">
              <Input
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                placeholder="Search study IDs or study names..."
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
            <Button
              variant="outline"
              size="sm"
              type="button"
              onClick={() => setRefreshToken((previous) => previous + 1)}
            >
              Refresh
            </Button>
          </div>
          <TablePagination
            canPrevious={canPrevious}
            canNext={canNext}
            isLoading={isLoading}
            onPrevious={() => setPageIndex((previous) => Math.max(previous - 1, 1))}
            onNext={() => setPageIndex((previous) => previous + 1)}
            pageIndex={pageIndex}
            pageCount={pageCount}
            pageSize={DEFAULT_PAGE_SIZE}
            currentCount={rows.length}
            totalCount={totalCount}
            itemLabel="study IDs"
          />
          <Table className="min-w-[1200px] table-auto [&_td]:px-3 [&_td]:py-2">
            <TableHeader>
              <TableRow className="border-b border-border/60">
                <TableHead>Study ID</TableHead>
                <TableHead>Study Name</TableHead>
                <TableHead>Group</TableHead>
                <TableHead>Age</TableHead>
                <TableHead>Sex</TableHead>
                <TableHead>Center</TableHead>
                <TableHead>Genotyping</TableHead>
                <TableHead>NOD2 Mutation</TableHead>
                <TableHead>IL23R Mutation</TableHead>
                <TableHead>Samples</TableHead>
                <TableHead>Files</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.length ? (
                rows.map((row) => (
                  <TableRow key={row.id} className="border-b border-border/40 last:border-none">
                    <TableCell className="whitespace-nowrap">{row.name}</TableCell>
                    <TableCell>{formatText(row.study_name_label || row.study_name)}</TableCell>
                    <TableCell>{formatText(row.study_group_label || row.study_group)}</TableCell>
                    <TableCell>{row.age ?? "-"}</TableCell>
                    <TableCell>{formatText(row.sex_label || row.sex)}</TableCell>
                    <TableCell>{formatText(row.study_center_label || row.study_center)}</TableCell>
                    <TableCell>{formatBoolean(row.genotype_data_available)}</TableCell>
                    <TableCell>{formatBoolean(row.nod2_mutation_present)}</TableCell>
                    <TableCell>{formatBoolean(row.il23r_mutation_present)}</TableCell>
                    <TableCell>
                      {row.sample_count > 0 ? (
                        <DropdownMenu
                          onOpenChange={(open) => {
                            if (open) {
                              void loadSamples(row);
                            }
                          }}
                        >
                          <DropdownMenuTrigger asChild>
                            <Button variant="secondary" size="sm" className="h-7 px-2 text-xs">
                              {row.sample_count} Sample(s)
                              <ChevronDown className="ml-1 h-3 w-3" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="start">
                            {samplesById[row.id]?.isLoading ? (
                              <DropdownMenuItem disabled>Loading samples...</DropdownMenuItem>
                            ) : samplesById[row.id]?.error ? (
                              <DropdownMenuItem disabled>
                                {samplesById[row.id]?.error ?? "Unable to load samples."}
                              </DropdownMenuItem>
                            ) : samplesById[row.id]?.loaded ? (
                              samplesById[row.id]?.items.length ? (
                                samplesById[row.id]?.items.map((sample) => (
                                  <DropdownMenuItem key={sample.id} asChild>
                                    <Link
                                      href={`/samples/${encodeURIComponent(sample.sample_id)}`}
                                      className="max-w-[240px] truncate"
                                    >
                                      {sample.sample_id} {sample.sample_type_label ?? ""}
                                    </Link>
                                  </DropdownMenuItem>
                                ))
                              ) : (
                                <DropdownMenuItem disabled>No samples found.</DropdownMenuItem>
                              )
                            ) : (
                              <DropdownMenuItem disabled>Loading samples...</DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      ) : (
                        <span className="text-muted-foreground">No samples</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {row.file_count > 0 ? (
                        <DropdownMenu
                          onOpenChange={(open) => {
                            if (open) {
                              void loadFiles(row);
                            }
                          }}
                        >
                          <DropdownMenuTrigger asChild>
                            <Button variant="secondary" size="sm" className="h-7 px-2 text-xs">
                              {row.file_count} File(s)
                              <ChevronDown className="ml-1 h-3 w-3" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="start">
                            {filesById[row.id]?.isLoading ? (
                              <DropdownMenuItem disabled>Loading files...</DropdownMenuItem>
                            ) : filesById[row.id]?.error ? (
                              <DropdownMenuItem disabled>
                                {filesById[row.id]?.error ?? "Unable to load files."}
                              </DropdownMenuItem>
                            ) : filesById[row.id]?.loaded ? (
                              filesById[row.id]?.items.length ? (
                                filesById[row.id]?.items.map((file) => (
                                  <DropdownMenuItem key={file.id} asChild>
                                    <Link
                                      href={`/datastore/read/${file.id}`}
                                      className="max-w-[240px] truncate"
                                    >
                                      {file.file_name ?? "File"}
                                    </Link>
                                  </DropdownMenuItem>
                                ))
                              ) : (
                                <DropdownMenuItem disabled>No files found.</DropdownMenuItem>
                              )
                            ) : (
                              <DropdownMenuItem disabled>Loading files...</DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      ) : (
                        <span className="text-muted-foreground">No files</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-2">
                        <Button asChild variant="link" size="sm" className="h-auto p-0">
                          <Link href={`/study_id/detail/${encodeURIComponent(row.name)}`}>
                            <Eye size={16} />
                            View
                          </Link>
                        </Button>
                        <Button asChild variant="link" size="sm" className="h-auto p-0">
                          <Link href={`/study_id/edit/${encodeURIComponent(row.name)}`}>
                            <Edit size={16} />
                            Edit
                          </Link>
                        </Button>
                        {isStaff ? (
                          <Button
                            type="button"
                            variant="link"
                            size="sm"
                            className="h-auto p-0"
                            onClick={() => openDeleteDialog(row)}
                          >
                            <span className="inline-flex items-center gap-1">
                              <Trash2 size={16} />
                              Delete
                            </span>
                          </Button>
                        ) : null}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={12} className="text-center text-muted-foreground">
                    {isLoading ? "Loading study IDs..." : "No study IDs found."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {errorMessage ? (
            <div className="rounded-md border border-destructive/50 bg-destructive/5 px-4 py-3 text-sm text-destructive">
              {errorMessage}
            </div>
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
            currentCount={rows.length}
            totalCount={totalCount}
            itemLabel="study IDs"
          />
        </CardContent>
      </Card>
      <Dialog
        open={deleteDialogOpen}
        onOpenChange={(open) => {
          if (open) {
            setDeleteDialogOpen(true);
            return;
          }
          closeDeleteDialog();
        }}
      >
        <DialogContent showCloseButton={!isDeleting}>
          <DialogHeader>
            <DialogTitle>Delete study ID?</DialogTitle>
            <DialogDescription>
              This will permanently remove{" "}
              <span className="font-semibold text-foreground">
                {deleteTarget?.name ?? "this ID"}
              </span>
              .
            </DialogDescription>
          </DialogHeader>
          {deleteError ? <p className="text-sm text-destructive">{deleteError}</p> : null}
          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={closeDeleteDialog}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={confirmDelete}
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Confirm delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
