import { useState, useEffect, useCallback } from "react";
import { useAppSelector } from "@/store/hooks";
import { listUsers, createUser, deactivateUser, updateUser } from "@/api/client";
import type { UserResponse } from "@/types";
import { Button } from "@/components/ui/button";
import { PaginationControls } from "@/components/PaginationControls";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  UserPlus,
  Pencil,
  Trash2,
  ShieldCheck,
  User as UserIcon,
  KeyRound,
} from "lucide-react";

type DialogMode = "create" | "edit-role" | "reset-password" | null;
type FormRole = "admin" | "staff" | "employee";
const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail ?? "Something went wrong. Please try again.";

export default function UserManagement() {
  const currentUser = useAppSelector((s) => s.auth.user);

  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Dialog state
  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);

  // Form fields
  const [formUsername, setFormUsername] = useState("");
  const [formFullName, setFormFullName] = useState("");
  const [formEmail, setFormEmail] = useState("");
  const [formPassword, setFormPassword] = useState("");
  const [formRole, setFormRole] = useState<FormRole>("employee");
  const [formMsg, setFormMsg] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<UserResponse | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listUsers();
      setUsers(data);
    } catch {
      setError("Failed to load users.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const totalPages = Math.max(1, Math.ceil(users.length / pageSize));
  const visibleUsers = users.slice((page - 1) * pageSize, page * pageSize);
  const changePageSize = (size: number) => {
    setPageSize(size);
    setPage(1);
  };

  const openCreate = () => {
    setFormUsername("");
    setFormFullName("");
    setFormEmail("");
    setFormPassword("");
    setFormRole("employee");
    setFormMsg("");
    setDialogMode("create");
  };

  const openEditRole = (u: UserResponse) => {
    setSelectedUser(u);
    setFormRole(u.role as FormRole);
    setFormMsg("");
    setDialogMode("edit-role");
  };

  const openResetPassword = (u: UserResponse) => {
    setSelectedUser(u);
    setFormPassword("");
    setFormMsg("");
    setDialogMode("reset-password");
  };

  const closeDialog = () => {
    setDialogMode(null);
    setSelectedUser(null);
    setFormMsg("");
  };

  const handleCreate = async () => {
    if (!formUsername.trim() || !formFullName.trim() || !formEmail.trim() || !formPassword.trim()) {
      setFormMsg("Name, email, username, and password are required.");
      return;
    }
    if (formPassword.length < 8) {
      setFormMsg("Password must be at least 8 characters.");
      return;
    }
    setSubmitting(true);
    try {
      await createUser({
        username: formUsername.trim(),
        full_name: formFullName.trim(),
        email: formEmail.trim(),
        password: formPassword,
        role: formRole,
      });
      closeDialog();
      fetchUsers();
    } catch (error) {
      setFormMsg(errorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditRole = async () => {
    if (!selectedUser) return;
    setSubmitting(true);
    try {
      await updateUser(selectedUser.id, { role: formRole });
      closeDialog();
      fetchUsers();
    } catch (error) {
      setFormMsg(errorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleResetPassword = async () => {
    if (!selectedUser) return;
    if (formPassword.length < 8) {
      setFormMsg("Password must be at least 8 characters.");
      return;
    }
    setSubmitting(true);
    try {
      await updateUser(selectedUser.id, { password: formPassword });
      closeDialog();
    } catch (error) {
      setFormMsg(errorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setSubmitting(true);
    try {
      await deactivateUser(deleteTarget.id);
      setDeleteTarget(null);
      fetchUsers();
    } catch (error) {
      setError(errorMessage(error));
      setDeleteTarget(null);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 md:gap-6 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
            User Management
          </h1>
          <p className="text-muted-foreground text-sm md:text-base">
            Manage application accounts and roles
          </p>
        </div>
        <Button onClick={openCreate} className="shrink-0">
          <UserPlus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-3 bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg text-sm">
          <span className="shrink-0">⚠</span>
          <span className="flex-1">{error}</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-xs"
            onClick={fetchUsers}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-1">
            <CardDescription>Total Users</CardDescription>
            <CardTitle className="text-3xl">{users.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardDescription>Admins</CardDescription>
            <CardTitle className="text-3xl">
              {users.filter((u) => u.role === "admin").length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardDescription>Staff</CardDescription>
            <CardTitle className="text-3xl">
              {users.filter((u) => u.role === "staff").length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardDescription>Employees</CardDescription>
            <CardTitle className="text-3xl">
              {users.filter((u) => u.role === "employee").length}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <p className="p-6 text-muted-foreground text-sm">Loading…</p>
          ) : users.length === 0 ? (
            <p className="p-6 text-muted-foreground text-sm">No users found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/40">
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      #
                    </th>
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      Username
                    </th>
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      Role
                    </th>
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      Created
                    </th>
                    <th className="py-3 px-4 text-right font-medium text-muted-foreground">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {visibleUsers.map((u, idx) => (
                    <tr
                      key={u.id}
                      className="border-b last:border-0 hover:bg-muted/20 transition-colors"
                    >
                      <td className="py-3 px-4 text-muted-foreground">
                        {(page - 1) * pageSize + idx + 1}
                      </td>
                      <td className="py-3 px-4 font-medium flex items-center gap-2">
                        {u.role === "admin" ? (
                          <ShieldCheck className="h-4 w-4 text-primary shrink-0" />
                        ) : (
                          <UserIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                        )}
                        {u.username}
                        {u.username === currentUser?.username && (
                          <span className="text-xs text-muted-foreground">
                            (you)
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={
                            u.role === "admin"
                              ? "default"
                              : u.role === "staff"
                                ? "secondary"
                                : "outline"
                          }
                          className="capitalize"
                        >
                          {u.role}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {formatDate(u.created_at)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openEditRole(u)}
                            title="Change role"
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openResetPassword(u)}
                            title="Reset password"
                          >
                            <KeyRound className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-destructive hover:text-destructive"
                            onClick={() => setDeleteTarget(u)}
                            disabled={u.username === currentUser?.username}
                            title="Deactivate user"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <PaginationControls
            page={page}
            pageSize={pageSize}
            totalItems={users.length}
            totalPages={totalPages}
            onPageChange={setPage}
            onPageSizeChange={changePageSize}
          />
        </CardContent>
      </Card>

      {/* ── Create User Dialog ── */}
      <Dialog
        open={dialogMode === "create"}
        onOpenChange={(o) => !o && closeDialog()}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New User</DialogTitle>
            <DialogDescription>
              Create a new application account
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <label className="text-sm font-medium">Username</label>
              <Input
                value={formUsername}
                onChange={(e) => setFormUsername(e.target.value)}
                placeholder="e.g. john_doe"
                autoFocus
              />
            </div>
            <div>
              <label className="text-sm font-medium">Full name</label>
              <Input
                value={formFullName}
                onChange={(e) => setFormFullName(e.target.value)}
                placeholder="e.g. John Doe"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Email</label>
              <Input
                type="email"
                value={formEmail}
                onChange={(e) => setFormEmail(e.target.value)}
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Password</label>
              <Input
                type="password"
                value={formPassword}
                onChange={(e) => setFormPassword(e.target.value)}
                placeholder="Min 8 characters"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Role</label>
              <select
                value={formRole}
                onChange={(e) => setFormRole(e.target.value as FormRole)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="employee">Employee</option>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {formMsg && <p className="text-sm text-destructive">{formMsg}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={submitting}>
              {submitting ? "Creating…" : "Create User"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Edit Role Dialog ── */}
      <Dialog
        open={dialogMode === "edit-role"}
        onOpenChange={(o) => !o && closeDialog()}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Role</DialogTitle>
            <DialogDescription>
              Update the role for <strong>{selectedUser?.username}</strong>
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <label className="text-sm font-medium">Role</label>
              <select
                value={formRole}
                onChange={(e) => setFormRole(e.target.value as FormRole)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="employee">Employee</option>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {formMsg && <p className="text-sm text-destructive">{formMsg}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>
              Cancel
            </Button>
            <Button onClick={handleEditRole} disabled={submitting}>
              {submitting ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Reset Password Dialog ── */}
      <Dialog
        open={dialogMode === "reset-password"}
        onOpenChange={(o) => !o && closeDialog()}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reset Password</DialogTitle>
            <DialogDescription>
              Set a new password for <strong>{selectedUser?.username}</strong>
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <label className="text-sm font-medium">New Password</label>
              <Input
                type="password"
                value={formPassword}
                onChange={(e) => setFormPassword(e.target.value)}
                placeholder="Min 6 characters"
                autoFocus
              />
            </div>
            {formMsg && <p className="text-sm text-destructive">{formMsg}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>
              Cancel
            </Button>
            <Button onClick={handleResetPassword} disabled={submitting}>
              {submitting ? "Saving…" : "Reset Password"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Delete Confirmation Dialog ── */}
      <Dialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deactivate User</DialogTitle>
            <DialogDescription>
              Are you sure you want to deactivate{" "}
              <strong>{deleteTarget?.username}</strong>? Their account will no
              longer be able to sign in.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={submitting}
            >
              {submitting ? "Deactivating…" : "Deactivate"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
