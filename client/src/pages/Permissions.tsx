import { useState } from "react";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import {
  saveRolePermissions,
  clearPermissionsError,
} from "@/store/slices/permissionsSlice";
import type { PermissionSet } from "@/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShieldCheck, ShieldAlert, Save, RefreshCw } from "lucide-react";

// ── Permission groups for display ─────────────────────────────────────────────

type PermKey = keyof PermissionSet;

interface PermGroup {
  label: string;
  items: Array<{ key: PermKey; label: string }>;
}

const PERMISSION_GROUPS: PermGroup[] = [
  {
    label: "Dashboard",
    items: [{ key: "canViewDashboard", label: "View Dashboard" }],
  },
  {
    label: "User Management",
    items: [
      { key: "canViewUserManagement", label: "View User Management" },
      { key: "canManageUsers", label: "Create / Edit / Delete Users" },
    ],
  },
  {
    label: "Settings",
    items: [{ key: "canViewSettings", label: "View Settings" }],
  },
  // Add your custom permission groups here
  // Example:
  // {
  //   label: 'Your Feature',
  //   items: [
  //     { key: 'canViewYourFeature', label: 'View Your Feature' },
  //     { key: 'canManageYourFeature', label: 'Manage Your Feature' },
  //   ],
  // },
];

const CONFIGURABLE_ROLES: Array<{
  role: string;
  label: string;
  description: string;
}> = [
  {
    role: "staff",
    label: "Staff",
    description: "Standard users with configurable access to features",
  },
  {
    role: "employee",
    label: "Employee",
    description: "Basic users with limited access",
  },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function Permissions() {
  const dispatch = useAppDispatch();
  const { rolePermissions, isSaving, error } = useAppSelector(
    (s) => s.permissions,
  );

  // local draft state: { staff: {...}, employee: {...} }
  const [drafts, setDrafts] = useState<Record<string, PermissionSet>>(() => ({
    staff: { ...rolePermissions.staff },
    employee: { ...rolePermissions.employee },
  }));
  const [savedRoles, setSavedRoles] = useState<string[]>([]);

  const toggle = (role: string, key: PermKey) => {
    setDrafts((prev) => ({
      ...prev,
      [role]: { ...prev[role], [key]: !prev[role][key] },
    }));
    setSavedRoles((r) => r.filter((x) => x !== role));
  };

  const handleSave = async (role: string) => {
    dispatch(clearPermissionsError());
    const result = await dispatch(
      saveRolePermissions({ role, permissions: drafts[role] }),
    );
    if (saveRolePermissions.fulfilled.match(result)) {
      setSavedRoles((r) => [...r.filter((x) => x !== role), role]);
    }
  };

  const handleReset = (role: string) => {
    setDrafts((prev) => ({ ...prev, [role]: { ...rolePermissions[role] } }));
    setSavedRoles((r) => r.filter((x) => x !== role));
  };

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 md:gap-6 md:p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
          Role Permissions
        </h1>
        <p className="text-muted-foreground text-sm md:text-base mt-1">
          Configure what each role can access. Admin always has full access.
        </p>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Admin — read-only info card */}
      <Card className="border-primary/30 bg-primary/5">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">Admin</CardTitle>
            <Badge variant="default" className="ml-auto">
              Full Access
            </Badge>
          </div>
          <CardDescription>
            Admins have unrestricted access to all features and cannot be
            restricted.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Configurable roles */}
      {CONFIGURABLE_ROLES.map(({ role, label, description }) => {
        const draft = drafts[role] ?? {};
        const isSavedOk = savedRoles.includes(role);

        return (
          <Card key={role}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2 flex-wrap">
                <ShieldAlert className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-base">{label}</CardTitle>
                <Badge variant="secondary" className="capitalize">
                  {role}
                </Badge>
                {isSavedOk && (
                  <Badge
                    variant="outline"
                    className="text-green-600 border-green-400 ml-auto"
                  >
                    Saved
                  </Badge>
                )}
              </div>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {PERMISSION_GROUPS.map((group) => (
                <div key={group.label}>
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
                    {group.label}
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {group.items.map(({ key, label: pLabel }) => (
                      <label
                        key={key}
                        className="flex items-center gap-3 rounded-md border px-3 py-2 cursor-pointer hover:bg-muted/40 transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={!!draft[key]}
                          onChange={() => toggle(role, key)}
                          className="h-4 w-4 accent-primary cursor-pointer"
                        />
                        <span className="text-sm">{pLabel}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}

              {/* Actions */}
              <div className="flex items-center gap-2 pt-2 border-t">
                <Button
                  size="sm"
                  onClick={() => handleSave(role)}
                  disabled={isSaving}
                >
                  <Save className="h-3.5 w-3.5 mr-1.5" />
                  {isSaving ? "Saving…" : "Save Changes"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleReset(role)}
                  disabled={isSaving}
                >
                  <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
                  Reset
                </Button>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
