import { useCallback, useEffect, useState } from "react";
import { useAppSelector } from "@/store/hooks";
import { listAdminProducts, listOrders, listLowStock } from "@/api/client";
import type { Order, Product } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import {
  Boxes,
  ClipboardList,
  Package,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

const money = (value: number | string, currency = "INR") =>
  `${currency === "INR" ? "₹" : currency} ${Number(value).toFixed(2)}`;

export default function Dashboard() {
  const user = useAppSelector((state) => state.auth.user);
  const [products, setProducts] = useState<Product[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [lowStockCount, setLowStockCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (user?.role !== "admin") {
      setLoading(false);
      return;
    }
    try {
      const [productData, orderData, lowStockData] = await Promise.all([
        listAdminProducts(),
        listOrders(),
        listLowStock(),
      ]);
      setProducts(productData.items);
      setOrders(orderData.items);
      setLowStockCount(lowStockData.length);
    } catch {
      setError("Unable to load the latest admin metrics.");
    } finally {
      setLoading(false);
    }
  }, [user?.role]);

  useEffect(() => {
    load();
  }, [load]);
  const revenue = orders.reduce((sum, order) => sum + Number(order.total), 0);

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Welcome back, {user?.username}!
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}
      {user?.role === "admin" ? (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {[
              ["Revenue", money(revenue)],
              ["Orders", orders.length],
              ["Products", products.length],
              ["Low stock", lowStockCount],
            ].map(([label, value]) => (
              <Card key={String(label)}>
                <CardContent className="pt-5">
                  <p className="text-sm text-muted-foreground">{label}</p>
                  <p className="mt-1 text-2xl font-bold">
                    {loading ? "—" : value}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
            <Card>
              <CardContent className="pt-6">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold">Recent orders</h2>
                    <p className="text-sm text-muted-foreground">
                      Latest activity across the store
                    </p>
                  </div>
                  <ClipboardList className="h-5 w-5 text-muted-foreground" />
                </div>
                {orders.length === 0 ? (
                  <p className="py-8 text-sm text-muted-foreground">
                    No orders to show.
                  </p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="bg-black text-white">
                          {["Order", "Status", "Total"].map((heading) => (
                            <th key={heading} className="px-3 py-2 font-medium">
                              {heading}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {orders.slice(0, 5).map((order, index) => (
                          <tr
                            key={order.id}
                            className={`border-t ${index % 2 === 0 ? "bg-[#efefef]/60 dark:bg-muted/30" : ""}`}
                          >
                            <td className="px-3 py-2 font-medium">
                              #{order.id}
                            </td>
                            <td className="px-3 py-2 capitalize text-muted-foreground">
                              {order.status.replaceAll("_", " ")}
                            </td>
                            <td className="px-3 py-2 font-semibold">
                              {money(order.total, order.currency)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold">Admin workspace</h2>
                    <p className="text-sm text-muted-foreground">
                      Core controls are ready
                    </p>
                  </div>
                  <ShieldCheck className="h-5 w-5 text-primary" />
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3">
                    <Package className="h-4 w-4 text-muted-foreground" />
                    <span>Catalog and publication controls</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Boxes className="h-4 w-4 text-muted-foreground" />
                    <span>Inventory adjustments with audit reason</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    <span>Order fulfillment status workflow</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <h2 className="font-semibold">Welcome back, {user?.username}</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Your dashboard access is ready. Use the navigation to open the
              areas assigned to your role.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
