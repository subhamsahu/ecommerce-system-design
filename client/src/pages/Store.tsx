import { useCallback, useEffect, useState } from "react";
import {
  CheckCircle2,
  Minus,
  Plus,
  Search,
  ShoppingBag,
  ShoppingCart,
  Store as StoreIcon,
  Trash2,
} from "lucide-react";
import {
  addCartItem,
  attemptPayment,
  checkout,
  getCart,
  listCategories,
  listProducts,
  removeCartItem,
  updateCartItem,
} from "@/api/client";
import type { Cart, Category, Order, Product } from "@/types";
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
type Address = {
  line1: string;
  line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
};
const emptyAddress: Address = {
  line1: "",
  line2: "",
  city: "",
  state: "",
  postal_code: "",
  country: "IN",
};

export default function Store() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [cart, setCart] = useState<Cart | null>(null);
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [loading, setLoading] = useState(true);
  const [busyProduct, setBusyProduct] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [cartOpen, setCartOpen] = useState(false);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [address, setAddress] = useState<Address>(emptyAddress);
  const [checkoutError, setCheckoutError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [completedOrder, setCompletedOrder] = useState<Order | null>(null);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await listProducts({
        search: search.trim() || undefined,
        category_id: categoryId ? Number(categoryId) : undefined,
        page_size: 100,
      });
      setProducts(result.items);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [categoryId, search]);

  const loadStore = useCallback(async () => {
    try {
      const [categoryData, cartData] = await Promise.all([
        listCategories(),
        getCart(),
      ]);
      setCategories(categoryData);
      setCart(cartData);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, []);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);
  useEffect(() => {
    loadStore();
  }, [loadStore]);

  const addProduct = async (product: Product) => {
    setBusyProduct(product.id);
    try {
      setCart(await addCartItem(product.id));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusyProduct(null);
    }
  };

  const changeQuantity = async (
    itemId: number,
    productId: number,
    quantity: number,
  ) => {
    try {
      setCart(
        quantity < 1
          ? await removeCartItem(itemId)
          : await updateCartItem(itemId, productId, quantity),
      );
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const startCheckout = () => {
    setCheckoutError("");
    setCheckoutOpen(true);
  };
  const submitCheckout = async () => {
    if (
      !address.line1.trim() ||
      !address.city.trim() ||
      !address.state.trim() ||
      !address.postal_code.trim()
    ) {
      setCheckoutError("Address, city, state, and postal code are required.");
      return;
    }
    setSubmitting(true);
    setCheckoutError("");
    try {
      const order = await checkout(
        {
          ...address,
          line1: address.line1.trim(),
          line2: address.line2.trim() || undefined,
          city: address.city.trim(),
          state: address.state.trim(),
          postal_code: address.postal_code.trim(),
        },
        `checkout-${Date.now()}`,
      );
      await attemptPayment(order.id);
      setCompletedOrder({ ...order, status: "paid" });
      setCart(await getCart());
      setCheckoutOpen(false);
      setCartOpen(false);
      setAddress(emptyAddress);
    } catch (err) {
      setCheckoutError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const cartCount =
    cart?.items.reduce((sum, item) => sum + item.quantity, 0) ?? 0;

  return (
    <div className="flex flex-1 flex-col gap-6 bg-muted/20 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold">
            <StoreIcon className="h-6 w-6 text-primary" />
            Store
          </h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Browse products and place a test order
          </p>
        </div>
        <Button onClick={() => setCartOpen(true)}>
          <ShoppingCart className="mr-2 h-4 w-4" />
          Cart{" "}
          {cartCount > 0 && (
            <span className="ml-1 rounded-full bg-primary-foreground px-1.5 text-xs text-primary">
              {cartCount}
            </span>
          )}
        </Button>
      </div>
      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <span className="flex-1">{error}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              loadProducts();
              loadStore();
            }}
          >
            Retry
          </Button>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-[220px] flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search products or SKU"
            className="pl-9"
          />
        </div>
        <select
          value={categoryId}
          onChange={(event) => setCategoryId(event.target.value)}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="">All categories</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <Skeleton key={index} className="h-52 rounded-xl" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center text-muted-foreground">
            <ShoppingBag className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="font-medium">No products available</p>
            <p className="mt-1 text-sm">Try another search or category.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {products.map((product) => (
            <Card key={product.id} className="overflow-hidden">
              <div className="flex h-28 items-center justify-center bg-primary/5">
                <ShoppingBag className="h-12 w-12 text-primary/30" />
              </div>
              <CardContent className="space-y-3 p-4">
                <div>
                  <p className="font-semibold">{product.name}</p>
                  <p className="mt-1 font-mono text-xs text-muted-foreground">
                    {product.sku}
                  </p>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold">
                    {money(product.price, product.currency)}
                  </span>
                  <span
                    className={`text-xs ${product.available_quantity ? "text-muted-foreground" : "font-medium text-destructive"}`}
                  >
                    {product.available_quantity
                      ? `${product.available_quantity} available`
                      : "Out of stock"}
                  </span>
                </div>
                <Button
                  className="w-full"
                  onClick={() => addProduct(product)}
                  disabled={
                    !product.available_quantity || busyProduct === product.id
                  }
                >
                  {busyProduct === product.id ? "Adding..." : "Add to cart"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
      +
      <Dialog open={cartOpen} onOpenChange={setCartOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Your Cart</DialogTitle>
            <DialogDescription>
              Review your items before checkout.
            </DialogDescription>
          </DialogHeader>
          {!cart?.items.length ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              Your cart is empty.
            </div>
          ) : (
            <div className="space-y-4">
              {cart.items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 border-b pb-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{item.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {money(item.unit_price)} each
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() =>
                        changeQuantity(
                          item.id,
                          item.product_id,
                          item.quantity - 1,
                        )
                      }
                    >
                      <Minus className="h-3 w-3" />
                    </Button>
                    <span className="w-7 text-center text-sm">
                      {item.quantity}
                    </span>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-7 w-7"
                      disabled={item.quantity >= item.available_quantity}
                      onClick={() =>
                        changeQuantity(
                          item.id,
                          item.product_id,
                          item.quantity + 1,
                        )
                      }
                    >
                      <Plus className="h-3 w-3" />
                    </Button>
                  </div>
                  <span className="w-20 text-right text-sm font-semibold">
                    {money(Number(item.unit_price) * item.quantity)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-destructive"
                    onClick={() => changeQuantity(item.id, item.product_id, 0)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              ))}
              <div className="flex justify-between border-t pt-3 text-lg font-bold">
                <span>Total</span>
                <span>{money(cart.total)}</span>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setCartOpen(false)}>
              Continue shopping
            </Button>
            <Button onClick={startCheckout} disabled={!cart?.items.length}>
              Checkout
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog open={checkoutOpen} onOpenChange={setCheckoutOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Checkout</DialogTitle>
            <DialogDescription>
              Enter a delivery address for this test order.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3">
            <Input
              placeholder="Address line 1"
              value={address.line1}
              onChange={(event) =>
                setAddress({ ...address, line1: event.target.value })
              }
            />
            <Input
              placeholder="Address line 2 (optional)"
              value={address.line2}
              onChange={(event) =>
                setAddress({ ...address, line2: event.target.value })
              }
            />
            <div className="grid grid-cols-2 gap-3">
              <Input
                placeholder="City"
                value={address.city}
                onChange={(event) =>
                  setAddress({ ...address, city: event.target.value })
                }
              />
              <Input
                placeholder="State"
                value={address.state}
                onChange={(event) =>
                  setAddress({ ...address, state: event.target.value })
                }
              />
            </div>
            <Input
              placeholder="Postal code"
              value={address.postal_code}
              onChange={(event) =>
                setAddress({ ...address, postal_code: event.target.value })
              }
            />
            {checkoutError && (
              <p className="text-sm text-destructive">{checkoutError}</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCheckoutOpen(false)}>
              Back
            </Button>
            <Button onClick={submitCheckout} disabled={submitting}>
              {submitting ? "Processing..." : `Pay ${money(cart?.total ?? 0)}`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={!!completedOrder}
        onOpenChange={(open) => !open && setCompletedOrder(null)}
      >
        <DialogContent className="max-w-sm text-center">
          <DialogHeader>
            <div className="mx-auto rounded-full bg-emerald-100 p-3 text-emerald-600">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <DialogTitle>Order placed</DialogTitle>
            <DialogDescription>
              Your payment was simulated successfully.
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Order #{completedOrder?.id} · {money(completedOrder?.total ?? 0)}
          </p>
          <DialogFooter>
            <Button className="w-full" onClick={() => setCompletedOrder(null)}>
              Continue shopping
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
