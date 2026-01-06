// frontend/app/samples/[sampleId]/page.tsx
// Server-side page that renders a detailed sample view mirroring the legacy Django layout.
// Provides sample metadata, processing stats, and audit history within the Next.js dashboard shell.

import { cookies } from "next/headers";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { HistoryPanel } from "@/components/history/history-panel";
import { AlertDescription, AlertSuccess } from "@/components/ui/alert";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";
import { resolveDashboardUser } from "@/lib/dashboard-user";
import { isJwtExpired } from "@/lib/jwt";

type SampleHistoryChangeResponse = {
  field: string;
  label: string;
  old: string | null;
  new: string | null;
};

type SampleHistoryEntryResponse = {
  timestamp: string;
  user: string | null;
  summary?: string | null;
  changes: SampleHistoryChangeResponse[];
};

type SampleHistoryResponse = {
  created: string;
  created_by: string | null;
  last_modified: string;
  last_modified_by: string | null;
  entries: SampleHistoryEntryResponse[];
};

type StudyIdentifierSummary = {
  id: number;
  name: string;
};

type SampleDetailResponse = {
  sample_id: string;
  study_name: string;
  study_name_label: string | null;
  study_identifier: StudyIdentifierSummary | null;
  music_timepoint: string | null;
  music_timepoint_label: string | null;
  marvel_timepoint: string | null;
  marvel_timepoint_label: string | null;
  sample_type: string;
  sample_type_label: string | null;
  sample_datetime: string;
  sample_location: string;
  sample_sublocation: string | null;
  sample_comments: string | null;
  is_used: boolean;
  processing_datetime: string | null;
  processing_time_minutes: number | null;
  frozen_datetime: string | null;
  sample_volume: string | null;
  sample_volume_units: string | null;
  sample_volume_units_label: string | null;
  freeze_thaw_count: number | null;
  haemolysis_reference: string | null;
  haemolysis_reference_label: string | null;
  biopsy_location: string | null;
  biopsy_location_label: string | null;
  biopsy_inflamed_status: string | null;
  biopsy_inflamed_status_label: string | null;
  qubit_cfdna_ng_ul: string | null;
  paraffin_block_key: string | null;
  created: string;
  created_by: string | null;
  last_modified: string;
  last_modified_by: string | null;
  history: SampleHistoryResponse;
};

type PageParams = {
  sampleId: string;
};

type PageSearchParams = {
  updated?: string;
};

type DetailRow = {
  label: string;
  value: string;
};

const datetimeFormatter = new Intl.DateTimeFormat("en-GB", {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function formatDateTime(value: string | null): string {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return datetimeFormatter.format(date);
}

function formatMaybe(value: string | number | null | undefined, fallback: string = "—"): string {
  if (value === null || value === undefined) {
    return fallback;
  }
  if (typeof value === "string" && value.trim() === "") {
    return fallback;
  }
  return String(value);
}

async function fetchSampleDetail(
  sampleId: string,
  token: string,
): Promise<SampleDetailResponse | null> {
  const response = await fetch(
    buildBackendUrl(`/api/v3/samples/${encodeURIComponent(sampleId)}/`),
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
    throw new Error(`Failed to load sample: ${response.status}`);
  }

  return (await response.json()) as SampleDetailResponse;
}

function buildDetailRows(sample: SampleDetailResponse): DetailRow[] {
  const timepoint =
    sample.music_timepoint_label ??
    sample.marvel_timepoint_label ??
    sample.music_timepoint ??
    sample.marvel_timepoint;

  return [
    {
      label: "Study Name",
      value: formatMaybe(sample.study_name_label ?? sample.study_name),
    },
    {
      label: "Sample ID",
      value: sample.sample_id,
    },
    {
      label: "Study ID",
      value: sample.study_identifier?.name ?? "—",
    },
    {
      label: "Timepoint",
      value: formatMaybe(timepoint, "N/A"),
    },
    {
      label: "Sample Location",
      value: formatMaybe(sample.sample_location),
    },
    {
      label: "Sample Sublocation",
      value: formatMaybe(sample.sample_sublocation),
    },
    {
      label: "Sample Type",
      value: formatMaybe(sample.sample_type_label ?? sample.sample_type),
    },
    {
      label: "Sample Datetime",
      value: formatDateTime(sample.sample_datetime),
    },
    {
      label: "Sample Comments",
      value: formatMaybe(sample.sample_comments),
    },
  ];
}

function buildProcessingRows(sample: SampleDetailResponse): DetailRow[] {
  const volumeUnits = sample.sample_volume_units_label ?? sample.sample_volume_units ?? "";
  const volume = sample.sample_volume
    ? `${sample.sample_volume}${volumeUnits ? ` ${volumeUnits}` : ""}`
    : null;
  const haemolysis = sample.haemolysis_reference_label ?? sample.haemolysis_reference;
  const biopsyLocation = sample.biopsy_location_label ?? sample.biopsy_location;
  const biopsyStatus = sample.biopsy_inflamed_status_label ?? sample.biopsy_inflamed_status;

  return [
    {
      label: "Processing Datetime",
      value: formatDateTime(sample.processing_datetime),
    },
    {
      label: "Frozen Datetime",
      value: formatDateTime(sample.frozen_datetime),
    },
    {
      label: "Sample Used?",
      value: sample.is_used ? "Yes" : "No",
    },
    {
      label: "Time Between Sampling and Processing",
      value:
        sample.processing_time_minutes !== null
          ? `${sample.processing_time_minutes} minutes`
          : "N/A",
    },
    {
      label: "Sample Volume Remaining",
      value: volume ? volume : "N/A",
    },
    {
      label: "Freeze Thaw Count",
      value: formatMaybe(sample.freeze_thaw_count, "0"),
    },
    {
      label: "Haemolysis Reference",
      value: formatMaybe(haemolysis, "N/A"),
    },
    {
      label: "Biopsy Location",
      value: formatMaybe(biopsyLocation, "N/A"),
    },
    {
      label: "Biopsy Inflamed Status",
      value: formatMaybe(biopsyStatus, "N/A"),
    },
    {
      label: "Qubit (ng/uL)",
      value: formatMaybe(sample.qubit_cfdna_ng_ul, "N/A"),
    },
    {
      label: "Paraffin Block Key",
      value: formatMaybe(sample.paraffin_block_key, "N/A"),
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

export default async function SampleDetailPage({
  params,
  searchParams,
}: {
  params: PageParams;
  searchParams?: PageSearchParams;
}) {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const user = resolveDashboardUser(token);
  const sampleId = params.sampleId;

  const sample = await fetchSampleDetail(sampleId, token);
  if (!sample) {
    notFound();
  }

  const sampleDetailRows = buildDetailRows(sample);
  const sampleProcessingRows = buildProcessingRows(sample);
  const historySummary = {
    created: sample.history.created,
    createdBy: sample.history.created_by,
    lastModified: sample.history.last_modified,
    lastModifiedBy: sample.history.last_modified_by,
  };
  const normalizeHistoryValue = (value: string | null) => {
    if (value === null) {
      return null;
    }
    const trimmed = value.trim();
    return trimmed ? trimmed : null;
  };
  const historyEntries = sample.history.entries.map((entry) => ({
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
  const showUpdatedMessage = searchParams?.updated === "1";

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/" />
        <SidebarInset>
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
                    <BreadcrumbLink href="/">Samples</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>{sample.sample_id}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6">
            <Link href="/" className="text-sm text-primary underline">
              ← Back to Samples
            </Link>
            {showUpdatedMessage ? (
              <AlertSuccess>
                <AlertDescription>Sample updated.</AlertDescription>
              </AlertSuccess>
            ) : null}
            <section className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2 space-y-6">
                <DetailCard
                  title="Sample Details"
                  description="Key identifiers and location information for this sample."
                  rows={sampleDetailRows}
                />
                <DetailCard
                  title="Sample Processing"
                  description="Processing metadata and laboratory handling notes."
                  rows={sampleProcessingRows}
                />
                <Button asChild className="w-full sm:w-auto">
                  <Link href={`/samples/${encodeURIComponent(sample.sample_id)}/edit?from=detail`}>
                    Edit sample
                  </Link>
                </Button>
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
