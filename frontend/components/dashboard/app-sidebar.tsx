// frontend/components/dashboard/app-sidebar.tsx
// Renders the primary navigation sidebar with grouped dashboard links.
// Exists so pages can share a single source of truth for sidebar items alongside the profile footer.

import {
  ArchiveIcon,
  Cloud,
  CloudUploadIcon,
  DatabaseIcon,
  FlaskRoundIcon,
  HomeIcon,
  IdCardIcon,
  PlusSquareIcon,
  QrCodeIcon,
  ShieldIcon,
  UsersIcon,
} from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

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
  SidebarRail,
} from "@/components/ui/sidebar";
import { NavUser } from "./nav-user";
import type { DashboardUser } from "./user-profile-menu";

type NavItem = {
  label: string;
  href: string;
  icon: ReactNode;
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
        label: "Add Multiple",
        href: "/samples/add-multiple",
        icon: <PlusSquareIcon className="size-4" />,
      },
      { label: "QR scan", href: "/samples/qr-scan", icon: <QrCodeIcon className="size-4" /> },
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
      { label: "Datastores", href: "/datastores", icon: <CloudUploadIcon className="size-4" /> },
      { label: "Study IDs", href: "/study-ids", icon: <IdCardIcon className="size-4" /> },
    ],
  },
  {
    title: "Admin",
    items: [
      { label: "Users", href: "/admin/users", icon: <UsersIcon className="size-4" /> },
      { label: "Admin", href: "/admin", icon: <ShieldIcon className="size-4" /> },
    ],
  },
];

type AppSidebarProps = {
  user: DashboardUser;
  activeHref?: string;
};

export function AppSidebar({ user, activeHref }: AppSidebarProps) {
  return (
    <Sidebar>
      <SidebarHeader className="px-4 py-3 text-sm font-semibold">G-Trac</SidebarHeader>
      <SidebarContent>
        {NAVIGATION.map((group) => (
          <SidebarGroup key={group.title}>
            <SidebarGroupLabel>{group.title}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={activeHref === item.href}>
                      <Link href={item.href} className="flex items-center gap-3">
                        {item.icon}
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
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
