// frontend/components/datasets/datasets-dashboard.tsx
// Renders the datasets dashboard cards, guides, status checks, and access lists.
// Exists to keep the datasets UI cohesive while fetching overview data from the Next.js API.

"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AlertDescription, AlertError, AlertSuccess } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { dateFormatter, timeFormatter } from "@/lib/formatters";

type DatasetSummary = {
  name: string;
  study_name: string;
  study_name_label: string | null;
  description: string;
  last_modified: string;
  access_count: number;
};

type StatusCheckSummary = {
  data_source: string;
  response_status: number;
  error_message: string | null;
  checked_at: string;
  recent_statuses: number[];
};

type AccessListUser = {
  first_name: string;
  last_name: string;
  email: string;
};

type DatasetsOverviewPayload = {
  datasets: DatasetSummary[];
  status_checks: StatusCheckSummary[];
  user_access_list: AccessListUser[];
  site_url: string;
  token: string | null;
};

type TokenResponse = {
  token?: string | null;
  detail?: string;
};

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "Unknown";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return `${dateFormatter.format(parsed)} ${timeFormatter.format(parsed)}`;
}

export function DatasetsDashboard() {
  const [overview, setOverview] = useState<DatasetsOverviewPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [token, setToken] = useState<string | null>(null);
  const [tokenBusy, setTokenBusy] = useState(false);
  const [tokenMessage, setTokenMessage] = useState<string | null>(null);
  const [tokenError, setTokenError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadOverview = async () => {
      setIsLoading(true);
      setLoadError(null);

      try {
        const response = await fetch("/api/dashboard/datasets/overview", { cache: "no-store" });
        const payload = (await response.json()) as DatasetsOverviewPayload;

        if (!response.ok) {
          throw new Error((payload as { detail?: string }).detail ?? "Failed to load datasets.");
        }

        if (isMounted) {
          setOverview(payload);
          setToken(payload.token ?? null);
        }
      } catch (error) {
        if (isMounted) {
          setLoadError(error instanceof Error ? error.message : "Failed to load datasets.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadOverview();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!overview || selectedDataset) {
      return;
    }
    if (overview.datasets.length > 0) {
      setSelectedDataset(overview.datasets[0].name);
    }
  }, [overview, selectedDataset]);

  const apiBaseUrl = useMemo(() => {
    if (!overview?.site_url) {
      return "";
    }
    return overview.site_url.endsWith("/") ? overview.site_url.slice(0, -1) : overview.site_url;
  }, [overview?.site_url]);

  const selectedApiUrl = useMemo(() => {
    if (!apiBaseUrl || !selectedDataset) {
      return "";
    }
    return `${apiBaseUrl}/api/v3/datasets/${encodeURIComponent(selectedDataset)}/`;
  }, [apiBaseUrl, selectedDataset]);

  const pythonToken = token ?? "<your-token>";
  const apiUrlValue = selectedApiUrl || "<select-a-dataset>";

  const pythonExample = `# This is a basic example - do not commit this code to git.

import requests
import pandas as pd

# Set the API_URL for the dataset you want to access
API_URL = '${apiUrlValue}'

GTRAC_API_TOKEN = '${pythonToken}'

authorization_header = {'Authorization': f'Token {GTRAC_API_TOKEN}'}
response = requests.get(API_URL, headers = authorization_header, timeout=30)
data = response.json()
df = pd.DataFrame(data)
`;

  const rExample = `library(httr)
library(jsonlite)

# Set the API_URL for the dataset you want to access
API_URL <- '${apiUrlValue}'

GTRAC_API_TOKEN <- "Token ${pythonToken}"

response <- httr::GET(API_URL, add_headers(Authorization = GTRAC_API_TOKEN))
json_result <- httr::content(response, as="text", encoding="utf-8")
df <- jsonlite::fromJSON(json_result)
`;

  const handleTokenAction = async (action: "create" | "refresh" | "delete") => {
    setTokenBusy(true);
    setTokenMessage(null);
    setTokenError(null);

    try {
      const endpoint =
        action === "refresh" ? "/api/dashboard/user-token/refresh" : "/api/dashboard/user-token";
      const method = action === "delete" ? "DELETE" : "POST";
      const response = await fetch(endpoint, { method, cache: "no-store" });
      const payload = (await response.json()) as TokenResponse;

      if (!response.ok) {
        throw new Error(payload.detail ?? "Unable to update the API token.");
      }

      if (action === "delete") {
        setToken(null);
        setTokenMessage("Token deleted.");
      } else {
        setToken(payload.token ?? null);
        setTokenMessage(action === "refresh" ? "Token refreshed." : "Token generated.");
      }
    } catch (error) {
      setTokenError(error instanceof Error ? error.message : "Unable to update the API token.");
    } finally {
      setTokenBusy(false);
    }
  };

  if (isLoading) {
    return (
      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Datasets</CardTitle>
              <CardDescription>Loading dataset metadata...</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </CardContent>
          </Card>
        </div>
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Datasets User Guide</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (loadError || !overview) {
    return (
      <AlertError>
        <AlertDescription>{loadError ?? "Unable to load datasets."}</AlertDescription>
      </AlertError>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
      <div className="flex flex-col gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Datasets</CardTitle>
            <CardDescription>
              Browse datasets, export CSVs, and view access history.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {overview.datasets.length === 0 ? (
              <p className="text-sm text-muted-foreground">No datasets yet.</p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {overview.datasets.map((dataset) => {
                  const apiUrl = `${apiBaseUrl}/api/v3/datasets/${encodeURIComponent(dataset.name)}/`;
                  const exportUrl = `/api/dashboard/datasets/${encodeURIComponent(dataset.name)}/export`;
                  const accessHistoryUrl = `/datasets/${encodeURIComponent(dataset.name)}/access-history`;

                  return (
                    <Card key={dataset.name} className="border-muted">
                      <CardHeader className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="secondary">
                            {dataset.study_name_label || dataset.study_name}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            Updated {formatDateTime(dataset.last_modified)}
                          </span>
                        </div>
                        <CardTitle className="text-lg">{dataset.name}</CardTitle>
                        {dataset.description ? (
                          <CardDescription>{dataset.description}</CardDescription>
                        ) : null}
                      </CardHeader>
                      <CardContent className="space-y-3 text-sm">
                        <div className="space-y-1">
                          <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                            API URL (JSON)
                          </div>
                          <Link
                            href={apiUrl}
                            target="_blank"
                            className="break-all text-primary hover:underline"
                          >
                            {apiUrl}
                          </Link>
                        </div>
                        <div className="flex flex-wrap items-center gap-3">
                          <Button size="sm" variant="secondary" asChild>
                            <Link href={exportUrl} target="_blank">
                              Download CSV
                            </Link>
                          </Button>
                          <Button size="sm" variant="ghost" asChild>
                            <Link href={accessHistoryUrl}>Access history</Link>
                          </Button>
                          <span className="text-xs text-muted-foreground">
                            Access count: {dataset.access_count}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col md:grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Datasets User Guide</CardTitle>
            <CardDescription>Helpful links and API access details.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 text-sm">
            <div className="space-y-2">
              <div className="font-medium">Documentation</div>
              <Button size="sm" variant="secondary" asChild>
                <Link href="https://shaunchuah.github.io/orca_docs/" target="_blank">
                  Documentation (opens in new window)
                </Link>
              </Button>
              <div className="pt-2">
                New to this workflow? Try the{" "}
                <Link
                  href="https://shaunchuah.github.io/software_engineering_for_science/"
                  target="_blank"
                  className="text-primary underline"
                >
                  beginner&apos;s tutorial
                </Link>
                .
              </div>
            </div>

            <div className="space-y-3">
              <div className="font-medium">Authentication</div>
              <pre className="whitespace-pre-wrap rounded-md bg-muted px-3 py-2 text-xs">
                {token ? token : "No token yet. Create one using the button below."}
              </pre>
              <div className="flex flex-wrap gap-2">
                {token ? (
                  <>
                    <Button
                      size="sm"
                      onClick={() => handleTokenAction("refresh")}
                      disabled={tokenBusy}
                    >
                      Renew Token
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleTokenAction("delete")}
                      disabled={tokenBusy}
                    >
                      Delete Token
                    </Button>
                  </>
                ) : (
                  <Button
                    size="sm"
                    onClick={() => handleTokenAction("create")}
                    disabled={tokenBusy}
                  >
                    Generate Token
                  </Button>
                )}
              </div>
              {tokenMessage ? (
                <AlertSuccess>
                  <AlertDescription>{tokenMessage}</AlertDescription>
                </AlertSuccess>
              ) : null}
              {tokenError ? (
                <AlertError>
                  <AlertDescription>{tokenError}</AlertDescription>
                </AlertError>
              ) : null}
              <pre className="whitespace-pre-wrap rounded-md bg-muted px-3 py-2 text-xs">
                Authorization: Token {pythonToken}
              </pre>
            </div>

            <div className="space-y-3">
              <div className="font-medium">Code Examples</div>
              <Select value={selectedDataset} onValueChange={setSelectedDataset}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a dataset" />
                </SelectTrigger>
                <SelectContent>
                  {overview.datasets.map((dataset) => (
                    <SelectItem key={dataset.name} value={dataset.name}>
                      {dataset.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="space-y-2">
                <div className="font-medium">Python</div>
                <pre className="whitespace-pre-wrap rounded-md bg-muted px-3 py-2 text-xs">
                  {pythonExample}
                </pre>
              </div>
              <div className="space-y-2">
                <div className="font-medium">R</div>
                <pre className="whitespace-pre-wrap rounded-md bg-muted px-3 py-2 text-xs">
                  {rExample}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Datasets Access List</CardTitle>
            <CardDescription>Users who currently have dataset access.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {overview.user_access_list.length === 0 ? (
              <p className="text-sm text-muted-foreground">No dataset users found.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {overview.user_access_list.map((user) => {
                    const fullName = `${user.first_name} ${user.last_name}`.trim();
                    return (
                      <TableRow key={user.email}>
                        <TableCell>{fullName || "Unknown"}</TableCell>
                        <TableCell>
                          <Link
                            href={`mailto:${user.email}`}
                            className="text-primary hover:underline"
                          >
                            {user.email}
                          </Link>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )}
            <div className="rounded-md border bg-muted/40 p-3 text-xs text-muted-foreground">
              Orca is our data orchestration platform using dagster. Visit{" "}
              <Link
                href="https://orca.musicstudy.uk/"
                target="_blank"
                className="text-primary underline"
              >
                https://orca.musicstudy.uk/
              </Link>
              . Data is refreshed every Monday to Friday night. Contact Shaun for credentials if
              needed.
            </div>
          </CardContent>
        </Card>
        {overview.status_checks.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>Data Source Connection Status</CardTitle>
              <CardDescription>
                Latest connectivity checks with the last 30 readings.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {overview.status_checks.map((check) => {
                const isHealthy = check.response_status === 200;
                const statusLabel = isHealthy
                  ? "200 OK"
                  : (check.error_message ?? `Status ${check.response_status}`);

                return (
                  <div key={check.data_source} className="space-y-2 rounded-lg border p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span
                          className={`h-2 w-2 rounded-full ${
                            isHealthy ? "bg-emerald-500" : "bg-rose-500"
                          }`}
                        />
                        <span className="font-medium">{check.data_source}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        Last checked {formatDateTime(check.checked_at)}
                      </span>
                    </div>
                    <div className={`text-sm ${isHealthy ? "text-emerald-700" : "text-rose-700"}`}>
                      {statusLabel}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {check.recent_statuses.map((status, index) => (
                        <span
                          key={`${check.data_source}-${index}`}
                          className={`h-2 w-2 rounded-full ${
                            status === 200 ? "bg-emerald-400" : "bg-rose-400"
                          }`}
                        />
                      ))}
                      <span className="ml-auto text-xs text-muted-foreground">Last 30 checks</span>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
