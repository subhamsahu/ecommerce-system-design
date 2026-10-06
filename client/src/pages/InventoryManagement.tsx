import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, Boxes, Plus } from "lucide-react";
import { adjustInventory, listAdminProducts, listLowStock } from "@/api/client";
import type { InventoryRecord, Product } from "@/types";
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
import { PaginationControls } from "@/components/PaginationControls";

const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail ?? "Something went wrong. Please try again.";

export default function InventoryManagement() {
  const [products, setProducts] = useState<Product[]>([]);
  const [lowStock, setLowStock] = useState<InventoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Product | null>(null);
  const [delta, setDelta] = useState("");
  const [reason, setReason] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [pagination, setPagination] = useState({ total_items: 0, total_pages: 0 });

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [productPage, lowStockData] = await Promise.all([
        listAdminProducts({ page, page_size: pageSize }),
        listLowStock(),
      ]);
      setProducts(productPage.items);
      setPagination(productPage.pagination);
      setLowStock(lowStockData);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page, pageSize]);
  useEffect(() => {
    load();
  }, [load]);

  const changePageSize = (size: number) => {
    setPageSize(size);
    setPage(1);
  };

  const openAdjustment = (product: Product) => {
    setSelected(product);
    setDelta("");
    setReason("");
    setDialogOpen(true);
  };
  const saveAdjustment = async () => {
    if (!selected || !delta || !reason.trim() || Number(delta) === 0) return;
    setSubmitting(true);
    try {
      await adjustInventory({
        product_id: selected.id,
        quantity_delta: Number(delta),
        reason: reason.trim(),
      });
      setDialogOpen(false);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const stockFor = (product: Product) => product.available_quantity ?? 0;
  const lowStockIds = new Set(lowStock.map((item) => item.product_id));

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold">
          <Boxes className="h-6 w-6 text-primary" />
          Inventory
        </h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Monitor stock and record controlled adjustments
        </p>
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
            <p className="text-sm text-muted-foreground">Tracked products</p>
            <p className="mt-1 text-2xl font-bold">{products.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Low stock alerts</p>
            <p className="mt-1 text-2xl font-bold text-amber-600">
              {lowStock.length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Units on hand</p>
            <p className="mt-1 text-2xl font-bold">
              {products.reduce((sum, product) => sum + stockFor(product), 0)}
            </p>
          </CardContent>
        </Card>
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
            <Boxes className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="font-medium">No inventory records yet</p>
          </div>
        ) : (
          <table className="w-full min-w-[700px] text-left text-sm">
            <thead>
              <tr className="bg-black text-white">
                {["Product", "SKU", "Available", "Threshold", "Health", ""].map(
                  (heading) => (
                    <th
                      key={heading}
                      className={`px-4 py-3 font-medium ${["Available", "Threshold", ""].includes(heading) ? "text-right" : ""}`}
                    >
                      {heading}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {products.map((product, index) => {
                const quantity = stockFor(product);
                const alert = lowStockIds.has(product.id);
                return (
                  <tr
                    key={product.id}
                    className={`border-t ${index % 2 === 0 ? "bg-[#efefef]/60 dark:bg-muted/30" : "bg-background"}`}
                  >
                    <td className="px-4 py-3 font-medium">{product.name}</td>
                    <td className="px-4 py-3 font-mono text-xs">
                      {product.sku}
                    </td>
                    <td
                      className={`px-4 py-3 text-right text-lg font-semibold ${alert ? "text-amber-600" : ""}`}
                    >
                      {quantity}
                    </td>
                    <td className="px-4 py-3 text-right text-muted-foreground">
                      {lowStock.find((item) => item.product_id === product.id)
                        ?.low_stock_threshold ?? 5}
                    </td>
                    <td className="px-4 py-3">
                      {alert ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                          <AlertTriangle className="h-3 w-3" />
                          Low stock
                        </span>
                      ) : (
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">
                          Healthy
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openAdjustment(product)}
                        >
                          <Plus className="mr-1 h-3.5 w-3.5" />
                          Adjust
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
        <PaginationControls
          page={page}
          pageSize={pageSize}
          totalItems={pagination.total_items}
          totalPages={pagination.total_pages}
          onPageChange={setPage}
          onPageSizeChange={changePageSize}
        />
      </div>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Adjust Inventory</DialogTitle>
            <DialogDescription>
              {selected?.name} ({selected?.sku})
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1">
              <label className="text-sm font-medium">Quantity change</label>
              <Input
                type="number"
                step="1"
                value={delta}
                onChange={(event) => setDelta(event.target.value)}
                placeholder="+10 or -2"
              />
              <p className="text-xs text-muted-foreground">
                Use a positive number to add stock or a negative number to
                remove it.
              </p>
            </div>
            <div className="grid gap-1">
              <label className="text-sm font-medium">Reason</label>
              <Input
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                placeholder="e.g. Supplier delivery"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={saveAdjustment}
              disabled={
                submitting || !delta || !reason.trim() || Number(delta) === 0
              }
            >
              {submitting ? "Updating..." : "Update Stock"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
