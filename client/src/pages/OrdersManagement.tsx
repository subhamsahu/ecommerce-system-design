import { useCallback, useEffect, useState } from "react";
import { ChevronDown, ClipboardList, Eye } from "lucide-react";
import { listOrders, updateOrderStatus } from "@/api/client";
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

const statuses = [
  "pending_payment",
  "paid",
  "processing",
  "shipped",
  "delivered",
  "cancelled",
  "refunded",
];
const money = (value: number | string, currency: string) =>
  `${currency === "INR" ? "₹" : currency} ${Number(value).toFixed(2)}`;
const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail ?? "Something went wrong. Please try again.";
const label = (value: string) =>
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export default function OrdersManagement() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Order | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setOrders(await listOrders());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    load();
  }, [load]);

  const changeStatus = async (order: Order, status: string) => {
    if (status === order.status) return;
    setSavingId(order.id);
    try {
      const updated = await updateOrderStatus(order.id, status);
      setOrders((current) =>
        current.map((item) => (item.id === order.id ? updated : item)),
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold">
          <ClipboardList className="h-6 w-6 text-primary" />
          Orders
        </h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Review customer orders and move them through fulfillment
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
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          ["All orders", orders.length],
          ["Paid", orders.filter((order) => order.status === "paid").length],
          [
            "Processing",
            orders.filter((order) => order.status === "processing").length,
          ],
          [
            "Delivered",
            orders.filter((order) => order.status === "delivered").length,
          ],
        ].map(([title, value]) => (
          <Card key={String(title)}>
            <CardContent className="pt-5">
              <p className="text-sm text-muted-foreground">{title}</p>
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
        ) : orders.length === 0 ? (
          <div className="py-16 text-center text-muted-foreground">
            <ClipboardList className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="font-medium">No orders yet</p>
          </div>
        ) : (
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead>
              <tr className="bg-black text-white">
                {["Order", "Placed", "Items", "Total", "Status", ""].map(
                  (heading) => (
                    <th
                      key={heading}
                      className={`px-4 py-3 font-medium ${["Items", "Total", ""].includes(heading) ? "text-right" : ""}`}
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
                    {new Date(order.created_at).toLocaleString("en-IN", {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {order.items.reduce((sum, item) => sum + item.quantity, 0)}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold">
                    {money(order.total, order.currency)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="relative w-44">
                      <select
                        value={order.status}
                        disabled={savingId === order.id}
                        onChange={(event) =>
                          changeStatus(order, event.target.value)
                        }
                        className="h-8 w-full appearance-none rounded-md border border-input bg-background px-2 pr-7 text-xs"
                      >
                        <option value={order.status}>
                          {label(order.status)}
                        </option>
                        {statuses
                          .filter((status) => status !== order.status)
                          .map((status) => (
                            <option key={status} value={status}>
                              {label(status)}
                            </option>
                          ))}
                      </select>
                      <ChevronDown className="pointer-events-none absolute right-2 top-2 h-4 w-4 text-muted-foreground" />
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        title="View order"
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
      </div>
      <Dialog
        open={!!selected}
        onOpenChange={(open) => !open && setSelected(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Order #{selected?.id}</DialogTitle>
            <DialogDescription>
              {selected &&
                new Date(selected.created_at).toLocaleString("en-IN", {
                  dateStyle: "long",
                  timeStyle: "short",
                })}
            </DialogDescription>
          </DialogHeader>
          {selected && (
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b pb-3">
                <span className="text-sm text-muted-foreground">Status</span>
                <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium">
                  {label(selected.status)}
                </span>
              </div>
              {selected.items.map((item) => (
                <div
                  key={`${item.sku}-${item.product_name}`}
                  className="flex items-center justify-between gap-4 text-sm"
                >
                  <div>
                    <p className="font-medium">{item.product_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.sku} · Qty {item.quantity}
                    </p>
                  </div>
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
