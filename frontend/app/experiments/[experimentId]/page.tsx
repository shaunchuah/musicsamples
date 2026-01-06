// frontend/app/experiments/[experimentId]/page.tsx
// Server-side page that renders a detailed experiment view mirroring the legacy Django layout.
// Provides experiment metadata and audit history within the Next.js dashboard shell.

import { cookies } from "next/headers";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { ExperimentEditDialogButton } from "@/components/experiments/experiment-edit-dialog-button";
import { HistoryPanel } from "@/components/history/history-panel";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";
import { resolveDashboardUser } from "@/lib/dashboard-user";
import { dateFormatter } from "@/lib/formatters";
import { isJwtExpired } from "@/lib/jwt";

type ExperimentHistoryChangeResponse = {
  field: string;
  label: string;
  old: string | null;
  new: string | null;
};

type ExperimentHistoryEntryResponse = {
  timestamp: string;
  user: string | null;
  summary?: string | null;
  changes: ExperimentHistoryChangeResponse[];
};

type ExperimentHistoryResponse = {
  created: string;
  created_by: string | null;
  last_modified: string;
  last_modified_by: string | null;
  entries: ExperimentHistoryEntryResponse[];
};

type ExperimentBoxSummary = {
  id: number;
  box_id: string;
};

type ExperimentDetailResponse = {
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
  created: string;
  created_by_email: string | null;
  last_modified: string;
  last_modified_by_email: string | null;
  history: ExperimentHistoryResponse;
};

type PageParams = {
  experimentId: string;
};

type DetailRow = {
  label: string;
  value: string;
};

function formatMaybe(value: string | null | undefined, fallback: string = "N/A"): string {
  if (!value || value.trim() === "") {
    return fallback;
  }
  return value;
}

function formatList(values: string[]): string {
  if (!values.length) {
    return "N/A";
  }
  return values.join(", ");
}

function formatDate(value: string | null): string {
  if (!value) {
    return "N/A";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return dateFormatter.format(parsed);
}

async function fetchExperimentDetail(
  experimentId: string,
  token: string,
): Promise<ExperimentDetailResponse | null> {
  const response = await fetch(
    buildBackendUrl(`/api/v3/experiments/${encodeURIComponent(experimentId)}/`),
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    },
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Failed to load experiment: ${response.status}`);
  }

  return (await response.json()) as ExperimentDetailResponse;
}

function buildDetailRows(experiment: ExperimentDetailResponse): DetailRow[] {
  return [
    { label: "Experiment Name", value: experiment.name },
    { label: "Experiment Date", value: formatDate(experiment.date) },
    {
      label: "Group",
      value: formatMaybe(experiment.basic_science_group_label ?? experiment.basic_science_group),
    },
    { label: "Description", value: formatMaybe(experiment.description) },
    { label: "Sample Types", value: formatList(experiment.sample_type_labels) },
    { label: "Tissue Types", value: formatList(experiment.tissue_type_labels) },
    {
      label: "Species",
      value: formatMaybe(experiment.species_label ?? experiment.species),
    },
    {
      label: "Boxes",
      value: experiment.boxes.length ? experiment.boxes.map((box) => box.box_id).join(", ") : "N/A",
    },
  ];
}

function DetailCard({
  title,
  description,
  rows,
}: {
  title: string;
  description?: string;
  rows: DetailRow[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full table-fixed border-collapse text-left text-sm">
          <tbody>
            {rows.map((row) => (
              <tr key={row.label} className="border-b border-border/40 last:border-none">
                <th className="w-1/3 px-2 py-2 font-semibold text-muted-foreground">{row.label}</th>
                <td className="px-2 py-2 whitespace-pre-line">{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

export default async function ExperimentDetailPage({ params }: { params: PageParams }) {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const user = resolveDashboardUser(token);
  const experiment = await fetchExperimentDetail(params.experimentId, token);

  if (!experiment) {
    notFound();
  }

  const detailRows = buildDetailRows(experiment);
  const historySummary = {
    created: experiment.history.created,
    createdBy: experiment.history.created_by,
    lastModified: experiment.history.last_modified,
    lastModifiedBy: experiment.history.last_modified_by,
  };
  const normalizeHistoryValue = (value: string | null) => {
    if (value === null) {
      return null;
    }
    const trimmed = value.trim();
    return trimmed ? trimmed : null;
  };
  const historyEntries = experiment.history.entries.map((entry) => ({
    timestamp: entry.timestamp,
    user: entry.user,
    summary: entry.summary ?? null,
    changes: entry.changes
      .map((change) => ({
        field: change.field,
        label: change.label,
        old: change.old,
        new: change.new,
      }))
      .filter((change) => {
        const normalizedOld = normalizeHistoryValue(change.old);
        const normalizedNew = normalizeHistoryValue(change.new);
        return normalizedOld !== null || normalizedNew !== null;
      }),
  }));

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/experiments" />
        <SidebarInset className="min-w-0">
          <header className="flex h-16 shrink-0 items-center gap-4 border-b px-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger className="-ml-1" />
              <Separator orientation="vertical" className="h-6" />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbLink href="/experiments">Experiments</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>{experiment.name}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6">
            <Link href="/experiments" className="text-sm text-primary underline">
              ← Back to Experiments List
            </Link>
            <section className="grid gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                <DetailCard
                  title="Experiment Details"
                  description="Identifiers, metadata, and linked boxes for this experiment."
                  rows={detailRows}
                />
                <ExperimentEditDialogButton
                  experiment={{
                    id: experiment.id,
                    basic_science_group: experiment.basic_science_group,
                    name: experiment.name,
                    description: experiment.description,
                    date: experiment.date,
                    species: experiment.species,
                    sample_types: experiment.sample_types,
                    tissue_types: experiment.tissue_types,
                  }}
                />
              </div>
              <div className="lg:col-span-1">
                <HistoryPanel
                  summary={historySummary}
                  entries={historyEntries}
                  description="Chronological log of updates applied to this record."
                />
              </div>
            </section>
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
