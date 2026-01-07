// frontend/app/boxes/[boxId]/page.tsx
// Server-side page that renders a detailed box view mirroring the legacy Django layout.
// Provides box metadata and audit history within the Next.js dashboard shell.

import { cookies } from "next/headers";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { BoxEditDialogButton } from "@/components/boxes/box-edit-dialog-button";
import { AppSidebar } from "@/components/dashboard/app-sidebar";
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
import { isJwtExpired } from "@/lib/jwt";
import DetailHeader from "@/components/ui/detail-header";

type BoxHistoryChangeResponse = {
  field: string;
  label: string;
  old: string | null;
  new: string | null;
};

type BoxHistoryEntryResponse = {
  timestamp: string;
  user: string | null;
  summary?: string | null;
  changes: BoxHistoryChangeResponse[];
};

type BoxHistoryResponse = {
  created: string;
  created_by: string | null;
  last_modified: string;
  last_modified_by: string | null;
  entries: BoxHistoryEntryResponse[];
};

type BoxExperimentSummary = {
  id: number;
  name: string;
  date: string | null;
};

type BoxDetailResponse = {
  id: number;
  box_id: string;
  basic_science_group: string;
  basic_science_group_label: string | null;
  experiments: BoxExperimentSummary[];
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
  created: string;
  created_by_email: string | null;
  last_modified: string;
  last_modified_by_email: string | null;
  history: BoxHistoryResponse;
};

type PageParams = {
  boxId: string;
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

async function fetchBoxDetail(boxId: string, token: string): Promise<BoxDetailResponse | null> {
  const response = await fetch(buildBackendUrl(`/api/v3/boxes/${encodeURIComponent(boxId)}/`), {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Failed to load box: ${response.status}`);
  }

  return (await response.json()) as BoxDetailResponse;
}

function buildDetailRows(box: BoxDetailResponse): DetailRow[] {
  return [
    { label: "Box ID", value: box.box_id },
    {
      label: "Group",
      value: formatMaybe(box.basic_science_group_label ?? box.basic_science_group),
    },
    {
      label: "Experiment IDs",
      value: box.experiments.length ? box.experiments.map((exp) => exp.name).join(", ") : "N/A",
    },
    { label: "Box Location", value: formatMaybe(box.location_label ?? box.location) },
    {
      label: "Box Sublocation",
      value: formatMaybe(
        box.sublocation ?? `${box.row ?? ""}${box.column ?? ""}${box.depth ?? ""}`.trim(),
      ),
    },
    { label: "Box Type", value: formatMaybe(box.box_type_label ?? box.box_type) },
    { label: "Sample Types", value: formatList(box.sample_type_labels) },
    { label: "Tissue Types", value: formatList(box.tissue_type_labels) },
    { label: "Comments", value: formatMaybe(box.comments) },
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

export default async function BoxDetailPage({ params }: { params: PageParams }) {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const user = resolveDashboardUser(token);
  const box = await fetchBoxDetail(params.boxId, token);

  if (!box) {
    notFound();
  }

  const detailRows = buildDetailRows(box);
  const historySummary = {
    created: box.history.created,
    createdBy: box.history.created_by,
    lastModified: box.history.last_modified,
    lastModifiedBy: box.history.last_modified_by,
  };
  const normalizeHistoryValue = (value: string | null) => {
    if (value === null) {
      return null;
    }
    const trimmed = value.trim();
    return trimmed ? trimmed : null;
  };
  const historyEntries = box.history.entries.map((entry) => ({
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
        <AppSidebar user={user} activeHref="/boxes" />
        <SidebarInset className="min-w-0">
          <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-4 border-b bg-muted/40 px-4 backdrop-blur supports-[backdrop-filter]:bg-muted/60">
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
                    <BreadcrumbLink href="/boxes">Boxes</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>{box.box_id}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6">
            <Link href="/boxes" className="text-sm text-primary underline">
              ← Back to Boxes List
            </Link>
            <DetailHeader category="Box" title={box.box_id} />
            <section className="grid gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                <DetailCard
                  title="Box Details"
                  description="Identifiers, location, and contents for this box."
                  rows={detailRows}
                />
                <BoxEditDialogButton box={box} />
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
