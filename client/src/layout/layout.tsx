import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { NotificationSidebar } from "@/components/notification-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useSettings } from "@/context/SettingsContext";
import { useAppDispatch } from "@/store/hooks";
import { loadRolePermissions } from "@/store/slices/permissionsSlice";
import { Button } from "@/components/ui/button";
import { Store as StoreIcon } from "lucide-react";

const PAGE_NAMES: Record<string, string> = {
  "/": "Dashboard",
  "/settings": "Settings",
  "/user-management": "User Management",
  "/permissions": "Role Permissions",
  "/store": "Store",
  // Add your custom page names here
  // Example:
  // '/your-page': 'Your Page Name',
};

export default function Layout() {
  const { compactMode } = useSettings();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Load role permissions from backend once on mount
  useEffect(() => {
    dispatch(loadRolePermissions());
  }, [dispatch]);

  const pageName = PAGE_NAMES[location.pathname] ?? "Dashboard";

  return (
    <SidebarProvider key={String(compactMode)} defaultOpen={!compactMode}>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="/">Application</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>{pageName}</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="ml-auto flex items-center gap-2 px-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/store")}
            >
              <StoreIcon className="mr-1.5 h-4 w-4" />
              Visit Store
            </Button>
            <NotificationSidebar />
          </div>
        </header>
        <Outlet />
      </SidebarInset>
    </SidebarProvider>
  );
}
