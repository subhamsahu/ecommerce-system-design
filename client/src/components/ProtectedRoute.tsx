import { type ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAppSelector } from "@/store/hooks";
import { getPermissions, type AppRole } from "@/hooks/usePermissions";
import type { PermissionSet } from "@/types";

interface ProtectedRouteProps {
  children: ReactNode;
  /** Redirect unless the user has one of these exact roles. Admin-only screens. */
  requireRole?: AppRole | AppRole[];
  /** Redirect unless the user's permission set has this flag set to true.
   *  Admin always bypasses this check (admin has all permissions). */
  requirePermission?: keyof PermissionSet;
}

export default function ProtectedRoute({
  children,
  requireRole,
  requirePermission,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAppSelector(
    (state) => state.auth,
  );
  const rolePermissions = useAppSelector((s) => s.permissions.rolePermissions);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Role-based guard (for strictly admin-only routes)
  if (requireRole) {
    const allowed = Array.isArray(requireRole) ? requireRole : [requireRole];
    if (!allowed.includes((user?.role ?? "") as AppRole)) {
      return <Navigate to="/forbidden" replace />;
    }
  }

  // Permission-based guard: admin always has full access; everyone else is checked
  if (requirePermission && user?.role !== "admin") {
    const perms = getPermissions(user?.role, rolePermissions);
    if (!perms[requirePermission]) {
      return <Navigate to="/forbidden" replace />;
    }
  }

  return <>{children}</>;
}
