import { useCallback, useEffect, useState } from "react";
import { FolderTree, Plus } from "lucide-react";
import { createCategory, listCategories } from "@/api/client";
import type { Category } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail ?? "Something went wrong. Please try again.";

export default function CategoryManagement() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setCategories(await listCategories());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setName("");
    setDescription("");
    setFormError("");
    setDialogOpen(true);
  };
  const save = async () => {
    if (!name.trim()) {
      setFormError("Category name is required.");
      return;
    }
    setSubmitting(true);
    setFormError("");
    try {
      await createCategory({
        name: name.trim(),
        description: description.trim() || undefined,
      });
      setDialogOpen(false);
      await load();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold">
            <FolderTree className="h-6 w-6 text-primary" />
            Categories
          </h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Organize products into clear catalog groups
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="mr-1 h-4 w-4" />
          Add Category
        </Button>
      </div>
      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <span className="flex-1">{error}</span>
          <Button variant="ghost" size="sm" onClick={load}>
            Retry
          </Button>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Total categories</p>
            <p className="mt-1 text-2xl font-bold">
              {loading ? "—" : categories.length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Active</p>
            <p className="mt-1 text-2xl font-bold text-emerald-600">
              {loading
                ? "—"
                : categories.filter((category) => category.is_active).length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Latest addition</p>
            <p className="mt-1 truncate text-lg font-semibold">
              {categories[0]?.name ?? "—"}
            </p>
          </CardContent>
        </Card>
      </div>
      <div className="overflow-x-auto rounded-md border">
        {loading ? (
          <div className="space-y-3 p-6">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-10" />
            ))}
          </div>
        ) : categories.length === 0 ? (
          <div className="py-16 text-center text-muted-foreground">
            <FolderTree className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="font-medium">No categories yet</p>
            <Button className="mt-4" onClick={openCreate}>
              Add First Category
            </Button>
          </div>
        ) : (
          <table className="w-full min-w-[620px] text-left text-sm">
            <thead>
              <tr className="bg-black text-white">
                {["Category", "Slug", "Description", "Created", "Status"].map(
                  (heading) => (
                    <th key={heading} className="px-4 py-3 font-medium">
                      {heading}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {categories.map((category, index) => (
                <tr
                  key={category.id}
                  className={`border-t ${index % 2 === 0 ? "bg-[#efefef]/60 dark:bg-muted/30" : "bg-background"}`}
                >
                  <td className="px-4 py-3 font-medium">{category.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                    {category.slug}
                  </td>
                  <td className="max-w-[320px] truncate px-4 py-3 text-muted-foreground">
                    {category.description || "No description"}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(category.created_at).toLocaleDateString("en-IN")}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${category.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}`}
                    >
                      {category.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Category</DialogTitle>
            <DialogDescription>
              Create a category for catalog organization.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1">
              <label className="text-sm font-medium">Name</label>
              <Input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. Accessories"
              />
            </div>
            <div className="grid gap-1">
              <label className="text-sm font-medium">Description</label>
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Optional description"
                className="min-h-20 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            {formError && (
              <p className="text-sm text-destructive">{formError}</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={save} disabled={submitting}>
              {submitting ? "Saving..." : "Add Category"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
