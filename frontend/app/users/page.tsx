// frontend/app/users/page.tsx
// Server-rendered staff user management page wrapping the client-side user table and dialogs.
// Exists to expose the Django user admin capabilities inside the Next.js dashboard at /users.

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { UserEmailListCard } from "@/components/users/user-email-list-card";
import { UsersTable } from "@/components/users/users-table";
import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";
import { isJwtExpired } from "@/lib/jwt";
import type { DashboardUser } from "@/types/dashboard";

type CurrentUserProfile = {
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  groups?: string[];
};

async function fetchCurrentUser(token: string): Promise<CurrentUserProfile | null> {
  try {
    const response = await fetch(buildBackendUrl("/api/v3/users/me/"), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Failed to load current user: ${response.status}`);
    }

    return (await response.json()) as CurrentUserProfile;
  } catch (error) {
    console.error("Unable to fetch current user for /users:", error);
    return null;
  }
}

function toDashboardUser(profile: CurrentUserProfile): DashboardUser {
  return {
    email: profile.email,
    firstName: profile.first_name,
    lastName: profile.last_name,
    isStaff: profile.is_staff,
    isSuperuser: profile.is_superuser,
    groups: profile.groups ?? [],
  };
}

export default async function UsersPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  const profile = await fetchCurrentUser(token);

  if (!profile) {
    redirect("/login");
  }

  if (!profile.is_staff) {
    redirect("/");
  }

  const user = toDashboardUser(profile);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-muted/40">
        <AppSidebar user={user} activeHref="/users" />
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
                    <BreadcrumbLink href="/users">Users</BreadcrumbLink>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <main className="flex min-w-0 flex-1 flex-col gap-6 p-6">
            <UserEmailListCard />
            <UsersTable />
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
// frontend/app/users/page.tsx
// Server-rendered staff user management page wrapping the client-side user table and dialogs.
// Exists to expose the Django user admin capabilities inside the Next.js dashboard at /users.
