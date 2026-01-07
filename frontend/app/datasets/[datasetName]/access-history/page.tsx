// frontend/app/datasets/[datasetName]/access-history/page.tsx
// Server-rendered access history view for a single dataset.
// Exists to mirror the legacy access history template inside the Next.js dashboard shell.

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";
import { resolveDashboardUser } from "@/lib/dashboard-user";
import { dateFormatter, timeFormatter } from "@/lib/formatters";
import { isJwtExpired } from "@/lib/jwt";

type AccessHistoryEntry = {
  user_label: string;
  user_email: string;
  access_type: string;
  accessed: string;
};

type AccessHistoryPayload = {
  dataset: string;
  access_count: number;
  results: AccessHistoryEntry[];
};

type PageProps = {
  params: {
    datasetName: string;
  };
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

async function fetchAccessHistory(
  token: string,
  datasetName: string,
): Promise<AccessHistoryPayload | null> {
  try {
    const response = await fetch(
      buildBackendUrl(`/api/v3/datasets/${encodeURIComponent(datasetName)}/access-history/`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        cache: "no-store",
      },
    );

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Failed to load dataset access history: ${response.status}`);
    }

    return (await response.json()) as AccessHistoryPayload;
  } catch (error) {
    console.error("Failed to load dataset access history:", error);
    return null;
  }
}

export default async function DatasetAccessHistoryPage({ params }: PageProps) {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const user = resolveDashboardUser(token);
  const datasetName = decodeURIComponent(params.datasetName);
  const data = await fetchAccessHistory(token, datasetName);

  if (!data) {
    redirect("/datasets");
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/datasets" />
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
                    <BreadcrumbLink href="/datasets">Datasets</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>Access History</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex min-w-0 flex-1 flex-col gap-6 p-6">
            <Card>
              <CardHeader>
                <CardTitle>Access History for {data.dataset}</CardTitle>
                <CardDescription>Access count: {data.access_count}</CardDescription>
              </CardHeader>
              <CardContent>
                {data.results.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No access history recorded yet.</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>User</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Access Type</TableHead>
                        <TableHead>Accessed</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.results.map((entry, index) => (
                        <TableRow key={`${entry.user_email}-${entry.accessed}-${index}`}>
                          <TableCell>{entry.user_label}</TableCell>
                          <TableCell>{entry.user_email}</TableCell>
                          <TableCell>{entry.access_type}</TableCell>
                          <TableCell>{formatDateTime(entry.accessed)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
