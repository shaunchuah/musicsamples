// frontend/app/samples/[sampleId]/edit/page.tsx
// Server-rendered page wrapper that loads sample data and renders the edit form.
// Exists to provide an authenticated edit surface within the Next.js dashboard.

import { cookies } from "next/headers";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { EditSampleForm } from "@/components/samples/edit-sample-form";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";
import { resolveDashboardUser } from "@/lib/dashboard-user";
import { isJwtExpired } from "@/lib/jwt";

type StudyIdentifierSummary = {
  id: number;
  name: string;
};

type SampleEditResponse = {
  sample_id: string;
  study_name: string;
  music_timepoint: string | null;
  marvel_timepoint: string | null;
  study_identifier: StudyIdentifierSummary | null;
  sample_type: string;
  sample_datetime: string | null;
  sample_location: string;
  sample_sublocation: string | null;
  sample_comments: string | null;
  processing_datetime: string | null;
  frozen_datetime: string | null;
  sample_volume: string | null;
  sample_volume_units: string | null;
  freeze_thaw_count: number | null;
  haemolysis_reference: string | null;
  biopsy_location: string | null;
  biopsy_inflamed_status: string | null;
  qubit_cfdna_ng_ul: string | null;
  paraffin_block_key: string | null;
};

type PageParams = {
  sampleId: string;
};

type PageSearchParams = {
  from?: string;
};

async function fetchSampleDetail(
  sampleId: string,
  token: string,
): Promise<SampleEditResponse | null> {
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

  return (await response.json()) as SampleEditResponse;
}

export default async function SampleEditPage({
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

  const from = searchParams?.from ?? "dashboard";
  const backHref = from === "detail" ? `/samples/${encodeURIComponent(sample.sample_id)}` : "/";
  const backLabel = from === "detail" ? "← Back to Sample" : "← Back to Samples";

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/" />
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
                    <BreadcrumbLink href="/">Samples</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbLink href={`/samples/${encodeURIComponent(sample.sample_id)}`}>
                      {sample.sample_id}
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>Edit</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6">
            <Link href={backHref} className="text-sm text-primary underline">
              {backLabel}
            </Link>
            <div className="w-full max-w-5xl">
              <EditSampleForm sampleId={sample.sample_id} initialData={sample} />
            </div>
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
