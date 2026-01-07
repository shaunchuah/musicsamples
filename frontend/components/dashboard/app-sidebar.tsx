// frontend/components/dashboard/app-sidebar.tsx
// Renders the primary navigation sidebar with grouped dashboard links.
// Exists so pages can share a single source of truth for sidebar items alongside the profile footer.

"use client";

import {
  ArchiveIcon,
  ChevronDownIcon,
  DatabaseIcon,
  FlaskRoundIcon,
  HomeIcon,
  IdCardIcon,
  MapPinIcon,
  PlusSquareIcon,
  QrCodeIcon,
  TrashIcon,
  UsersIcon,
} from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { useDashboardUser } from "@/components/dashboard/user-profile-provider";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import type { DashboardUser } from "@/types/dashboard";
import { NavUser } from "./nav-user";

type NavItem = {
  label: string;
  href?: string;
  icon: ReactNode;
  items?: NavItem[];
};

type NavGroup = {
  title: string;
  items: NavItem[];
};

const NAVIGATION: NavGroup[] = [
  {
    title: "Samples",
    items: [
      { label: "Dashboard", href: "/", icon: <HomeIcon className="size-4" /> },
      {
        label: "QR Scan",
        icon: <QrCodeIcon className="size-4" />,
        items: [
          {
            label: "Add Multiple",
            href: "/samples/qr-scan/add-multiple",
            icon: <PlusSquareIcon className="size-4" />,
          },
          {
            label: "Update Location",
            href: "/samples/qr-scan/update-location",
            icon: <MapPinIcon className="size-4" />,
          },
          {
            label: "Mark Used",
            href: "/samples/qr-scan/mark-used",
            icon: <TrashIcon className="size-4" />,
          },
        ],
      },
    ],
  },
  {
    title: "Box Tracking",
    items: [
      { label: "Boxes", href: "/boxes", icon: <ArchiveIcon className="size-4" /> },
      { label: "Experiments", href: "/experiments", icon: <FlaskRoundIcon className="size-4" /> },
    ],
  },
  {
    title: "Data Management",
    items: [
      { label: "Datasets", href: "/datasets", icon: <DatabaseIcon className="size-4" /> },
      // { label: "Datastores", href: "/datastores", icon: <CloudUploadIcon className="size-4" /> },
    ],
  },
  {
    title: "Admin",
    items: [
      { label: "Users", href: "/users", icon: <UsersIcon className="size-4" /> },
      { label: "Study IDs", href: "/study-ids", icon: <IdCardIcon className="size-4" /> },
      // { label: "Admin", href: "/admin", icon: <ShieldIcon className="size-4" /> },
    ],
  },
];

type AppSidebarProps = {
  user: DashboardUser;
  activeHref?: string;
};

function buildInitialOpenState(
  activeHref: string | undefined,
  navigation: NavGroup[],
): Record<string, boolean> {
  const initialState: Record<string, boolean> = {};
  navigation.forEach((group) => {
    group.items.forEach((item) => {
      if (item.items?.length) {
        initialState[item.label] = item.items.some((subItem) => subItem.href === activeHref);
      }
    });
  });
  initialState["QR Scan"] = true;
  return initialState;
}

export function AppSidebar({ user, activeHref }: AppSidebarProps) {
  const { user: cachedUser } = useDashboardUser();
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const combinedUser = useMemo<DashboardUser>(() => {
    const effectiveUser = isHydrated ? cachedUser : null;
    const groups = Array.isArray(effectiveUser?.groups)
      ? effectiveUser?.groups
      : Array.isArray(user.groups)
        ? user.groups
        : [];

    return {
      ...user,
      ...(effectiveUser ?? {}),
      isStaff: effectiveUser?.isStaff ?? user.isStaff ?? false,
      isSuperuser: effectiveUser?.isSuperuser ?? user.isSuperuser ?? false,
      groups,
    };
  }, [cachedUser, isHydrated, user]);

  const navigation = useMemo<NavGroup[]>(() => {
    if (combinedUser.isStaff || combinedUser.isSuperuser) {
      return NAVIGATION;
    }

    const groupNames = (combinedUser.groups ?? []).map((group) => group.toLowerCase());
    const hasGroup = (name: string) => groupNames.includes(name.toLowerCase());

    const canSeeBoxes = hasGroup("basic_science");
    const canSeeDatasets = hasGroup("datasets");

    return NAVIGATION.map((group) => {
      if (group.title === "Admin") {
        return { ...group, items: [] };
      }

      if (group.title === "Box Tracking") {
        return canSeeBoxes ? group : { ...group, items: [] };
      }

      if (group.title === "Data Management") {
        const items = group.items.filter((item) => {
          if (item.label === "Datasets") {
            return canSeeDatasets;
          }
          return true;
        });
        return { ...group, items };
      }

      return group;
    }).filter((group) => group.items.length > 0);
  }, [combinedUser]);

  const [openItems, setOpenItems] = useState<Record<string, boolean>>(() =>
    buildInitialOpenState(activeHref, navigation),
  );

  useEffect(() => {
    if (!activeHref) {
      return;
    }

    setOpenItems((prev) => {
      let changed = false;
      const next = { ...prev };
      navigation.forEach((group) => {
        group.items.forEach((item) => {
          if (item.items?.some((subItem) => subItem.href === activeHref)) {
            if (!next[item.label]) {
              next[item.label] = true;
              changed = true;
            }
          }
        });
      });
      return changed ? next : prev;
    });
  }, [activeHref, navigation]);

  return (
    <Sidebar>
      <SidebarHeader className="px-4 py-3 text-sm font-semibold">G-Trac</SidebarHeader>
      <SidebarContent>
        {navigation.map((group) => (
          <SidebarGroup key={group.title}>
            <SidebarGroupLabel>{group.title}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => {
                  if (item.items?.length) {
                    const isActiveParent = item.items.some(
                      (subItem) => activeHref === subItem.href,
                    );
                    const isOpen = openItems[item.label] ?? isActiveParent;
                    return (
                      <SidebarMenuItem key={item.label}>
                        <SidebarMenuButton
                          isActive={isActiveParent}
                          aria-expanded={isOpen}
                          onClick={() =>
                            setOpenItems((prev) => ({
                              ...prev,
                              [item.label]: !isOpen,
                            }))
                          }
                        >
                          <span className="flex items-center gap-3">
                            {item.icon}
                            <span>{item.label}</span>
                          </span>
                          <ChevronDownIcon
                            className={`ml-auto size-4 transition-transform ${
                              isOpen ? "rotate-180" : ""
                            }`}
                          />
                        </SidebarMenuButton>
                        {isOpen ? (
                          <SidebarMenuSub>
                            {item.items.map((subItem) => (
                              <SidebarMenuSubItem key={subItem.href}>
                                <SidebarMenuSubButton
                                  asChild
                                  isActive={activeHref === subItem.href}
                                >
                                  <Link
                                    href={subItem.href ?? "#"}
                                    className="flex items-center gap-2"
                                  >
                                    {subItem.icon}
                                    <span>{subItem.label}</span>
                                  </Link>
                                </SidebarMenuSubButton>
                              </SidebarMenuSubItem>
                            ))}
                          </SidebarMenuSub>
                        ) : null}
                      </SidebarMenuItem>
                    );
                  }

                  return (
                    <SidebarMenuItem key={item.href}>
                      <SidebarMenuButton asChild isActive={activeHref === item.href}>
                        <Link href={item.href ?? "#"} className="flex items-center gap-3">
                          {item.icon}
                          <span>{item.label}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
