/**
 * usePermissions – role-based permission helpers.
 *
 * Permissions for 'staff' and 'employee' are loaded from the backend and
 * can be edited by an admin via the Permissions page.
 * 'admin' always has full access and cannot be changed.
 */

import { useNavigate } from "react-router-dom";
import { useAppSelector } from "@/store/hooks";
import type { PermissionSet } from "@/types";
import { DEFAULT_ROLE_PERMISSIONS } from "@/store/slices/permissionsSlice";

export type { PermissionSet };
export type AppRole = "admin" | "staff" | "employee";

/** Returns the permission set for a given role from the Redux store map. */
export function getPermissions(
  role: string | undefined | null,
  rolePermissions: Record<string, PermissionSet>,
): PermissionSet {
  const key = (role ?? "employee") as AppRole;
  return rolePermissions[key] ?? DEFAULT_ROLE_PERMISSIONS.employee;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function usePermissions() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAppSelector((s) => s.auth);
  const rolePermissions = useAppSelector((s) => s.permissions.rolePermissions);

  const perms = getPermissions(user?.role, rolePermissions);

  const isAdmin = user?.role === "admin";
  const isStaff = user?.role === "staff";
  const isEmployee = user?.role === "employee";

  const redirectToHome = () => navigate("/");

  const checkPermission = (hasPermission: boolean): boolean => {
    if (!isAuthenticated || !hasPermission) {
      redirectToHome();
      return false;
    }
    return true;
  };

  return {
    ...perms,
    isAdmin,
    isStaff,
    isEmployee,
    isAuthenticated,
    checkPermission,
    redirectToHome,
  };
}
