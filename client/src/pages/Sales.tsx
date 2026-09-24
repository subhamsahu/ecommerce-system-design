import { useCallback, useEffect, useState } from "react";
import { Eye, ShoppingCart } from "lucide-react";
import { listOrders } from "@/api/client";
import type { Order } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { PaginationControls } from "@/components/PaginationControls";

const money = (value: number | string, currency = "INR") =>
  `${currency === "INR" ? "₹" : currency} ${Number(value).toFixed(2)}`;

export default function Sales() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Order | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [pagination, setPagination] = useState({ total_items: 0, total_pages: 0 });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await listOrders({ page, page_size: pageSize });
      setOrders(result.items);
      setPagination(result.pagination);
    } catch {
      setError("Unable to load sales data.");
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

  const revenue = orders.reduce((sum, order) => sum + Number(order.total), 0);
  const units = orders.reduce(
    (sum, order) =>
      sum + order.items.reduce((itemSum, item) => itemSum + item.quantity, 0),
    0,
  );

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold">
          <ShoppingCart className="h-6 w-6 text-primary" />
          Sales
        </h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Revenue and order activity from completed checkouts
        </p>
      </div>
      {error && (
        <div className="rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Total revenue</p>
            <p className="mt-1 text-2xl font-bold">{money(revenue)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Orders</p>
            <p className="mt-1 text-2xl font-bold">{orders.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm text-muted-foreground">Units sold</p>
            <p className="mt-1 text-2xl font-bold">{units}</p>
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
        ) : (
          <table className="w-full min-w-[680px] text-left text-sm">
            <thead>
              <tr className="bg-black text-white">
                {["Order", "Date", "Items", "Status", "Revenue", ""].map(
                  (heading) => (
                    <th
                      key={heading}
                      className={`px-4 py-3 font-medium ${["Items", "Revenue", ""].includes(heading) ? "text-right" : ""}`}
                    >
                      {heading}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {orders.map((order, index) => (
                <tr
                  key={order.id}
                  className={`border-t ${index % 2 === 0 ? "bg-[#efefef]/60 dark:bg-muted/30" : "bg-background"}`}
                >
                  <td className="px-4 py-3 font-semibold">#{order.id}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(order.created_at).toLocaleDateString("en-IN")}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {order.items.reduce((sum, item) => sum + item.quantity, 0)}
                  </td>
                  <td className="px-4 py-3 capitalize text-muted-foreground">
                    {order.status.replaceAll("_", " ")}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-green-700">
                    {money(order.total, order.currency)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        title="View sale"
                        onClick={() => setSelected(order)}
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
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
      <Dialog
        open={!!selected}
        onOpenChange={(open) => !open && setSelected(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Order #{selected?.id}</DialogTitle>
            <DialogDescription>Sale detail</DialogDescription>
          </DialogHeader>
          {selected && (
            <div className="space-y-3">
              {selected.items.map((item) => (
                <div key={item.sku} className="flex justify-between text-sm">
                  <span>
                    {item.product_name} x {item.quantity}
                  </span>
                  <span>
                    {money(
                      Number(item.unit_price) * item.quantity,
                      selected.currency,
                    )}
                  </span>
                </div>
              ))}
              <div className="flex justify-between border-t pt-3 font-semibold">
                <span>Total</span>
                <span>{money(selected.total, selected.currency)}</span>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
