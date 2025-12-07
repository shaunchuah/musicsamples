// frontend/components/dashboard/nav-user.tsx
// Renders the sidebar profile trigger wired to backend identity data and logout behaviour.
// Exists so the dashboard can display accurate user metadata and allow sign-out in place.

"use client";

import { ChevronsUpDown, CreditCard, LogOut, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import type { DashboardUser } from "@/types/dashboard";

type NavUserProps = {
  user: DashboardUser & {
    avatar?: string | null;
  };
};

type UserProfileResponse = {
  email?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  is_staff?: boolean;
  is_superuser?: boolean;
  groups?: unknown;
};

type HydratedUser = DashboardUser & {
  groups?: string[] | null;
  avatar?: string | null;
};

function normaliseGroups(groups: unknown): string[] {
  if (Array.isArray(groups)) {
    return groups.filter((value): value is string => typeof value === "string");
  }
  return [];
}

function normaliseUserProfile(payload: UserProfileResponse): HydratedUser {
  return {
    email: typeof payload.email === "string" ? payload.email : null,
    firstName: typeof payload.first_name === "string" ? payload.first_name : null,
    lastName: typeof payload.last_name === "string" ? payload.last_name : null,
    isStaff: Boolean(payload.is_staff),
    isSuperuser: Boolean(payload.is_superuser),
    groups: normaliseGroups(payload.groups),
  };
}

function getInitials({ firstName, lastName, email }: DashboardUser): string {
  const fallback = email?.trim()?.[0]?.toUpperCase();
  const firstInitial = firstName?.trim()?.[0];
  const lastInitial = lastName?.trim()?.[0];
  const initials = [firstInitial, lastInitial].filter(Boolean).join("");
  return initials || fallback || "?";
}

function getFullName({ firstName, lastName }: DashboardUser): string {
  const parts = [firstName?.trim(), lastName?.trim()].filter(Boolean);
  return parts.length > 0 ? parts.join(" ") : "Unnamed User";
}

function resolveAccessLevel(details: HydratedUser): "superuser" | "staff" | "user" {
  if (details.isSuperuser) {
    return "superuser";
  }
  if (details.isStaff) {
    return "staff";
  }

  const groups = details.groups ?? [];
  if (groups.some((group) => typeof group === "string" && group.toLowerCase().includes("staff"))) {
    return "staff";
  }

  return "user";
}

function formatAccessLabel(level: "superuser" | "staff" | "user"): string {
  switch (level) {
    case "superuser":
      return "Superuser access";
    case "staff":
      return "Staff access";
    default:
      return "Standard access";
  }
}

export function NavUser({ user }: NavUserProps) {
  const router = useRouter();
  const { isMobile } = useSidebar();
  const [serverUser, setServerUser] = useState<HydratedUser | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    let isActive = true;

    async function fetchUserProfile() {
      try {
        const response = await fetch("/api/dashboard/user", {
          cache: "no-store",
        });
        if (!response.ok) {
          return;
        }
        const payload = (await response.json()) as UserProfileResponse;
        if (!isActive) {
          return;
        }
        setServerUser(normaliseUserProfile(payload));
      } catch {
        // Ignore fetch failures and fall back to existing prop data.
      } finally {
      }
    }

    void fetchUserProfile();
    return () => {
      isActive = false;
    };
  }, []);

  const combinedUser = useMemo<HydratedUser>(() => {
    const groups = Array.isArray(serverUser?.groups)
      ? serverUser?.groups
      : Array.isArray(user.groups)
        ? user.groups
        : [];

    return {
      email: serverUser?.email ?? user.email ?? null,
      firstName: serverUser?.firstName ?? user.firstName ?? null,
      lastName: serverUser?.lastName ?? user.lastName ?? null,
      isStaff: serverUser?.isStaff ?? user.isStaff ?? false,
      isSuperuser: serverUser?.isSuperuser ?? user.isSuperuser ?? false,
      groups,
      accessLevel: user.accessLevel,
      avatar: user.avatar ?? null,
    };
  }, [serverUser, user]);

  const name = getFullName(combinedUser);
  const email = combinedUser.email ?? "placeholder@example.com";
  const initials = getInitials(combinedUser);
  const accessLevel = combinedUser.accessLevel ?? resolveAccessLevel(combinedUser);
  const accessLabel = formatAccessLabel(accessLevel);

  const handleLogout = useCallback(async () => {
    setIsLoggingOut(true);
    try {
      const response = await fetch("/api/auth/logout", { method: "POST" });
      if (!response.ok) {
        setIsLoggingOut(false);
        return;
      }
      router.replace("/login");
      router.refresh();
    } catch {
      setIsLoggingOut(false);
    }
  }, [router]);

  const logoutLabel = isLoggingOut ? "Signing out..." : "Log out";

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="h-8 w-8 rounded-lg">
                <AvatarImage src={combinedUser.avatar ?? undefined} alt={name} />
                <AvatarFallback className="rounded-lg">{initials}</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">{name}</span>
                <span className="truncate text-xs text-muted-foreground">{email}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarImage src={combinedUser.avatar ?? undefined} alt={name} />
                  <AvatarFallback className="rounded-lg">{initials}</AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">{name}</span>
                  <span className="truncate text-xs text-muted-foreground">{email}</span>
                  <span className="truncate text-[11px] text-muted-foreground">{accessLabel}</span>
                </div>
              </div>
            </DropdownMenuLabel>

            <DropdownMenuGroup>
              <DropdownMenuItem>
                <ShieldCheck />
                Account
              </DropdownMenuItem>
              <DropdownMenuItem>
                <CreditCard />
                Change Password
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="cursor-pointer"
              onSelect={(event) => {
                event.preventDefault();
                if (!isLoggingOut) {
                  void handleLogout();
                }
              }}
            >
              <LogOut />
              {logoutLabel}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
