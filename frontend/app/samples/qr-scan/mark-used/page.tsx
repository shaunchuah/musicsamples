// frontend/app/samples/qr-scan/mark-used/page.tsx
// Server-rendered page wrapper for the QR scan mark-used workflow in the dashboard.
// Exists to provide authenticated access and shared shell layout for marking samples as used.

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { MarkUsedForm } from "@/components/samples/mark-used-form";
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

export default async function MarkUsedPage() {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const user = resolveDashboardUser(token);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/samples/qr-scan/mark-used" />
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
                    <BreadcrumbLink href="/">Samples</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>QR scan</BreadcrumbPage>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>Mark used</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex flex-1 flex-col gap-6 p-6">
            <div className="w-full max-w-5xl">
              <MarkUsedForm />
            </div>
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
