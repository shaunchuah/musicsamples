"use client";

import * as React from "react";
import {
  BookOpen,
  Bot,
  Settings2,
  SquareTerminal,
} from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";

import { useSession } from "next-auth/react";
import NavLogo from "./nav-logo";

// This is sample data.
const data = {

  navMain: [
    {
      title: "Samples",
      url: "#",
      icon: SquareTerminal,
      isActive: true,
      items: [
        {
          title: "Dashboard",
          url: "/samples/dashboard",
        },
        {
          title: "Add Multiple",
          url: "/samples/qr_scan/add_multiple",
        },
        {
          title: "QR Scan",
          url: "/samples/qr_scan",
        },
        {
          title: "Data Export",
          url: "/samples/data_export",
        },
        {
          title: "Used Samples",
          url: "/samples/used_samples",
        },
      ],
    },
    {
      title: "Files",
      url: "#",
      icon: Bot,
      items: [
        {
          title: "Dashboard",
          url: "/files/dashboard",
        },
      ],
    },
    {
      title: "Datasets",
      url: "#",
      icon: BookOpen,
      items: [
        {
          title: "Dashboard",
          url: "#",
        },
        {
          title: "Documentation",
          url: "#",
        },
      ],
    },
    {
      title: "Admin",
      url: "#",
      icon: Settings2,
      items: [
        {
          title: "Users",
          url: "users",
        },
        {
          title: "Django Admin",
          url: "https://samples.musicstudy.uk/admin/",
        },

      ],
    },
  ],

};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { data: session } = useSession();

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <NavLogo />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        {session?.user && (
          <NavUser
            user={{
              first_name: session.user.first_name ?? "Unknown User",
              last_name: session.user.last_name ?? "",
              email: session.user.email ?? "",
            }}
          />
        )}
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
