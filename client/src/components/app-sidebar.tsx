"use client";

import { LayoutDashboard, Users, Settings, Package } from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useAppSelector } from "@/store/hooks";
import { getPermissions } from "@/hooks/usePermissions";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const user = useAppSelector((state) => state.auth.user);
  const rolePermissions = useAppSelector((s) => s.permissions.rolePermissions);
  const perms = getPermissions(user?.role, rolePermissions);

  // Build navigation items dynamically based on permissions
  const navItems = [
    // Dashboard — only if canViewDashboard
    ...(perms.canViewDashboard
      ? [
          {
            title: "Dashboard",
            url: "/",
            icon: LayoutDashboard,
            isActive: true,
            items: [{ title: "Overview", url: "/" }],
          },
        ]
      : []),
    // Admin section
    ...(perms.canViewUserManagement
      ? [
          {
            title: "Administration",
            url: "/user-management",
            icon: Users,
            items: [
              { title: "Users", url: "/user-management" },
              { title: "Permissions", url: "/permissions" },
            ],
          },
        ]
      : []),
    ...(user?.role === "admin"
      ? [
          {
            title: "Operations",
            url: "/products",
            icon: Package,
            items: [
              { title: "Products", url: "/products" },
              { title: "Categories", url: "/categories" },
              { title: "Inventory", url: "/inventory" },
              { title: "Orders", url: "/orders" },
              { title: "Sales", url: "/sales" },
            ],
          },
        ]
      : []),
    // Settings section
    ...(perms.canViewSettings
      ? [
          {
            title: "Settings",
            url: "/settings",
            icon: Settings,
            items: [{ title: "General", url: "/settings" }],
          },
        ]
      : []),
    // Add your custom navigation items here
    // Example:
    // ...(perms.canViewYourFeature
    //   ? [{
    //     title: "Your Feature",
    //     url: "/your-feature",
    //     icon: YourIcon,
    //     items: [{ title: "Sub-item", url: "/your-feature" }],
    //   }]
    //   : []),
  ];

  const navUser = {
    name: user?.username ?? "User",
    email: user?.role ?? "employee",
    avatar: "",
  };

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex items-center gap-2 py-2">
          <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <LayoutDashboard className="size-4" />
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <span className="truncate font-semibold">Commerce Admin</span>
            <span className="truncate text-xs">Operations console</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navItems} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={navUser} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
