// frontend/components/dashboard/nav-user.tsx
// Renders the sidebar profile trigger wired to backend identity data and logout behaviour.
// Exists so the dashboard can display accurate user metadata and allow sign-out in place.

"use client";

import { ChevronsUpDown, CreditCard, LogOut, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AccountSettingsDialog } from "@/components/auth/account-settings-dialog";
import { ChangePasswordDialog } from "@/components/auth/change-password-dialog";
import { useDashboardUser } from "@/components/dashboard/user-profile-provider";
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

type HydratedUser = DashboardUser & {
  groups?: string[] | null;
  avatar?: string | null;
};

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
  const { user: cachedUser, setUser } = useDashboardUser();
  const [isHydrated, setIsHydrated] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isAccountOpen, setIsAccountOpen] = useState(false);
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const combinedUser = useMemo<HydratedUser>(() => {
    const effectiveUser = isHydrated ? cachedUser : null;
    const groups = Array.isArray(effectiveUser?.groups)
      ? effectiveUser?.groups
      : Array.isArray(user.groups)
        ? user.groups
        : [];

    return {
      email: effectiveUser?.email ?? user.email ?? null,
      firstName: effectiveUser?.firstName ?? user.firstName ?? null,
      lastName: effectiveUser?.lastName ?? user.lastName ?? null,
      isStaff: effectiveUser?.isStaff ?? user.isStaff ?? false,
      isSuperuser: effectiveUser?.isSuperuser ?? user.isSuperuser ?? false,
      groups,
      accessLevel: effectiveUser?.accessLevel ?? user.accessLevel,
      avatar: user.avatar ?? null,
    };
  }, [cachedUser, isHydrated, user]);

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
      setUser(null);
      router.replace("/login");
      router.refresh();
    } catch {
      setIsLoggingOut(false);
    }
  }, [router, setUser]);

  const logoutLabel = isLoggingOut ? "Signing out..." : "Log out";

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground cursor-pointer"
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
              <DropdownMenuItem
                className="cursor-pointer"
                onSelect={(event) => {
                  event.preventDefault();
                  setIsAccountOpen(true);
                }}
              >
                <ShieldCheck />
                Account
              </DropdownMenuItem>
              <DropdownMenuItem
                className="cursor-pointer"
                onSelect={(event) => {
                  event.preventDefault();
                  setIsChangePasswordOpen(true);
                }}
              >
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
      <AccountSettingsDialog
        open={isAccountOpen}
        onOpenChange={setIsAccountOpen}
        onProfileUpdated={(profile) => {
          const nextUser: DashboardUser = {
            ...(cachedUser ?? {}),
            firstName:
              typeof profile.first_name === "string"
                ? profile.first_name
                : (cachedUser?.firstName ?? null),
            lastName:
              typeof profile.last_name === "string"
                ? profile.last_name
                : (cachedUser?.lastName ?? null),
          };
          setUser(nextUser);
        }}
      />
      <ChangePasswordDialog open={isChangePasswordOpen} onOpenChange={setIsChangePasswordOpen} />
    </SidebarMenu>
  );
}
