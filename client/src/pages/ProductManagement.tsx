import { useCallback, useEffect, useState } from "react";
import { Archive, Eye, EyeOff, Package, Pencil, Plus } from "lucide-react";
import {
  createProduct,
  listAdminProducts,
  listCategories,
  updateProduct,
} from "@/api/client";
import type { Category, Product } from "@/types";
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

const money = (value: number | string, currency = "INR") =>
  `${currency === "INR" ? "₹" : currency} ${Number(value).toFixed(2)}`;
const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail ?? "Something went wrong. Please try again.";

type ProductForm = {
  name: string;
  sku: string;
  description: string;
  price: string;
  category_id: string;
  currency: string;
};
const emptyForm: ProductForm = {
  name: "",
  sku: "",
  description: "",
  price: "",
  category_id: "",
  currency: "INR",
};

export default function ProductManagement() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form, setForm] = useState<ProductForm>(emptyForm);
  const [publishOnCreate, setPublishOnCreate] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [productData, categoryData] = await Promise.all([
        listAdminProducts(),
        listCategories(),
      ]);
      setProducts(productData);
      setCategories(categoryData);
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
    setEditing(null);
    setForm(emptyForm);
    setPublishOnCreate(true);
    setFormError("");
    setDialogOpen(true);
  };
  const openEdit = (product: Product) => {
    setEditing(product);
    setForm({
      name: product.name,
      sku: product.sku,
      description: product.description ?? "",
      price: String(product.price),
      category_id: product.category_id ? String(product.category_id) : "",
      currency: product.currency,
    });
    setPublishOnCreate(product.is_published);
    setFormError("");
    setDialogOpen(true);
  };

  const saveProduct = async () => {
    if (!form.name.trim() || !form.sku.trim() || !form.price) {
      setFormError("Name, SKU, and price are required.");
      return;
    }
    setSubmitting(true);
    setFormError("");
    try {
      const payload = {
        name: form.name.trim(),
        sku: form.sku.trim(),
        description: form.description.trim() || undefined,
        price: Number(form.price),
        currency: form.currency,
        category_id: form.category_id ? Number(form.category_id) : null,
      };
      if (editing)
        await updateProduct(editing.id, {
          ...payload,
          is_published: editing.is_published,
          is_archived: editing.is_archived,
        });
      else {
        const created = await createProduct(payload);
        if (publishOnCreate)
          await updateProduct(created.id, { is_published: true });
      }
      setDialogOpen(false);
      await load();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const togglePublished = async (product: Product) => {
    try {
      await updateProduct(product.id, { is_published: !product.is_published });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold">
            <Package className="h-6 w-6 text-primary" />
            Catalog
          </h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Manage products, pricing, and publication status
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="mr-1 h-4 w-4" />
          Add Product
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
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          ["Total Products", products.length],
          [
            "Published",
            products.filter((p) => p.is_published && !p.is_archived).length,
          ],
          [
            "Drafts",
            products.filter((p) => !p.is_published && !p.is_archived).length,
          ],
          ["Archived", products.filter((p) => p.is_archived).length],
        ].map(([label, value]) => (
          <Card key={String(label)}>
            <CardContent className="pt-5">
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="mt-1 text-2xl font-bold">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="overflow-x-auto rounded-md border">
        {loading ? (
          <div className="space-y-3 p-6">
            {Array.from({ length: 5 }).map((_, index) => (
              <Skeleton key={index} className="h-10" />
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="py-16 text-center text-muted-foreground">
            <Package className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="font-medium">No products yet</p>
            <Button className="mt-4" onClick={openCreate}>
              Add First Product
            </Button>
          </div>
        ) : (
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead>
              <tr className="bg-black text-white">
                {[
                  "Product",
                  "SKU",
                  "Category",
                  "Price",
                  "Stock",
                  "Status",
                  "",
                ].map((heading) => (
                  <th
                    key={heading}
                    className={`px-4 py-3 font-medium ${["Price", "Stock", ""].includes(heading) ? "text-right" : ""}`}
                  >
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {products.map((product, index) => (
                <tr
                  key={product.id}
                  className={`border-t ${index % 2 === 0 ? "bg-[#efefef]/60 dark:bg-muted/30" : "bg-background"}`}
                >
                  <td className="px-4 py-3">
                    <div className="font-medium">{product.name}</div>
                    <div className="max-w-[260px] truncate text-xs text-muted-foreground">
                      {product.description || "No description"}
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{product.sku}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {categories.find(
                      (category) => category.id === product.category_id,
                    )?.name ?? "Uncategorized"}
                  </td>
                  <td className="px-4 py-3 text-right font-medium">
                    {money(product.price, product.currency)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {product.available_quantity ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${product.is_archived ? "bg-slate-100 text-slate-600" : product.is_published ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}
                    >
                      {product.is_archived
                        ? "Archived"
                        : product.is_published
                          ? "Published"
                          : "Draft"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        title="Edit product"
                        onClick={() => openEdit(product)}
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      {!product.is_archived && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          title={
                            product.is_published
                              ? "Unpublish product"
                              : "Publish product"
                          }
                          onClick={() => togglePublished(product)}
                        >
                          {product.is_published ? (
                            <EyeOff className="h-3.5 w-3.5" />
                          ) : (
                            <Eye className="h-3.5 w-3.5" />
                          )}
                        </Button>
                      )}
                      {product.is_archived && (
                        <Archive className="mr-2 mt-1 h-3.5 w-3.5 text-muted-foreground" />
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing ? "Edit Product" : "Add Product"}
            </DialogTitle>
            <DialogDescription>
              Keep catalog details accurate for customers and operations.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3 py-2">
            <div className="grid gap-1">
              <label className="text-sm font-medium">Product name</label>
              <Input
                value={form.name}
                onChange={(event) =>
                  setForm({ ...form, name: event.target.value })
                }
              />
            </div>
            <div className="grid gap-1">
              <label className="text-sm font-medium">SKU</label>
              <Input
                value={form.sku}
                disabled={!!editing}
                onChange={(event) =>
                  setForm({ ...form, sku: event.target.value })
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1">
                <label className="text-sm font-medium">Price</label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.price}
                  onChange={(event) =>
                    setForm({ ...form, price: event.target.value })
                  }
                />
              </div>
              <div className="grid gap-1">
                <label className="text-sm font-medium">Category</label>
                <select
                  value={form.category_id}
                  onChange={(event) =>
                    setForm({ ...form, category_id: event.target.value })
                  }
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="">Uncategorized</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid gap-1">
              <label className="text-sm font-medium">Description</label>
              <textarea
                value={form.description}
                onChange={(event) =>
                  setForm({ ...form, description: event.target.value })
                }
                className="min-h-20 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            {!editing && (
              <label className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm">
                <input
                  type="checkbox"
                  checked={publishOnCreate}
                  onChange={(event) => setPublishOnCreate(event.target.checked)}
                  className="h-4 w-4 accent-primary"
                />
                Publish product to the store
              </label>
            )}
            {formError && (
              <p className="text-sm text-destructive">{formError}</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={saveProduct} disabled={submitting}>
              {submitting ? "Saving..." : "Save Product"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
