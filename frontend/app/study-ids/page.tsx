// frontend/app/study-ids/page.tsx
// Server-rendered page wrapper for the study IDs dashboard experience.
// Exists to provide authenticated access and the shared dashboard shell for study ID listings.

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { StudyIdsTable } from "@/components/study-ids/study-ids-table";
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
import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { resolveDashboardUser } from "@/lib/dashboard-user";
import { isJwtExpired } from "@/lib/jwt";

export default async function StudyIdsPage() {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const user = resolveDashboardUser(token);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/study-ids" />
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
                    <BreadcrumbPage>Study IDs</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6">
            <StudyIdsTable />
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
