/**
 * Axios instance and API helper functions.
 * All calls go through the Vite proxy (/api → localhost:8000).
 */

import axios from "axios";
import type {
  Category,
  Cart,
  InventoryRecord,
  Order,
  Payment,
  Product,
  ProductPage,
  ProductPayload,
  ProductUpdatePayload,
  Token,
  UserResponse,
  RolePermissionsMap,
  PermissionSet,
  OrderPage,
} from "@/types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  headers: { "Content-Type": "application/json" },
});

// Attach JWT to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  },
);

/* -------------------- Auth -------------------- */

export const loginUser = async (
  username: string,
  password: string,
): Promise<Token> => {
  const { data } = await api.post<Token>("/api/v1/auth/login", {
    username,
    password,
  });
  return data;
};

/* -------------------- User Management -------------------- */

export const listUsers = async (): Promise<UserResponse[]> => {
  const { data } = await api.get<UserResponse[]>("/api/v1/users");
  return data;
};

export const createUser = async (payload: {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role: string;
}): Promise<UserResponse> => {
  const { data } = await api.post<UserResponse>("/api/v1/users", payload);
  return data;
};

export const updateUser = async (
  id: number,
  payload: { role?: string; password?: string; is_active?: boolean },
): Promise<UserResponse> => {
  const { data } = await api.patch<UserResponse>(
    `/api/v1/users/${id}`,
    payload,
  );
  return data;
};

export const deactivateUser = async (id: number): Promise<UserResponse> => {
  return updateUser(id, { is_active: false });
};

/* -------------------- Role Permissions -------------------- */

export const getRolePermissions = async (): Promise<RolePermissionsMap> => {
  const { data } = await api.get<RolePermissionsMap>("/permissions");
  return data;
};

export const updateRolePermissions = async (
  role: string,
  permissions: PermissionSet,
): Promise<PermissionSet> => {
  const { data } = await api.put<PermissionSet>(`/permissions/${role}`, {
    permissions,
  });
  return data;
};

export const listCategories = async (): Promise<Category[]> => {
  const { data } = await api.get<Category[]>("/api/v1/categories");
  return data;
};

export const listAdminCategories = async (): Promise<Category[]> => {
  const { data } = await api.get<Category[]>("/api/v1/admin/categories");
  return data;
};

export const createCategory = async (payload: {
  name: string;
  description?: string;
}): Promise<Category> => {
  const { data } = await api.post<Category>(
    "/api/v1/admin/categories",
    payload,
  );
  return data;
};

export const listAdminProducts = async (
  params: { page?: number; page_size?: number } = {},
): Promise<ProductPage> => {
  const { data } = await api.get<ProductPage | Product[]>("/api/v1/admin/products", {
    params: { page: 1, page_size: 20, ...params },
  });
  return Array.isArray(data)
    ? { items: data, pagination: { page: 1, page_size: data.length, total_items: data.length, total_pages: 1 } }
    : data;
};

export const createProduct = async (
  payload: ProductPayload,
): Promise<Product> => {
  const { data } = await api.post<Product>("/api/v1/admin/products", payload);
  return data;
};

export const updateProduct = async (
  id: number,
  payload: ProductUpdatePayload,
): Promise<Product> => {
  const { data } = await api.patch<Product>(
    `/api/v1/admin/products/${id}`,
    payload,
  );
  return data;
};

export const listLowStock = async (): Promise<InventoryRecord[]> => {
  const { data } = await api.get<InventoryRecord[]>(
    "/api/v1/admin/inventory/low-stock",
  );
  return data;
};

export const adjustInventory = async (payload: {
  product_id: number;
  quantity_delta: number;
  reason: string;
}): Promise<InventoryRecord> => {
  const { data } = await api.post<InventoryRecord>(
    "/api/v1/admin/inventory/adjustments",
    payload,
  );
  return data;
};

export const listOrders = async (
  params: { page?: number; page_size?: number; status?: string } = {},
): Promise<OrderPage> => {
  const { data } = await api.get<OrderPage | Order[]>("/api/v1/orders", {
    params: { page: 1, page_size: 20, ...params },
  });
  return Array.isArray(data)
    ? { items: data, pagination: { page: 1, page_size: data.length, total_items: data.length, total_pages: 1 } }
    : data;
};

export const updateOrderStatus = async (
  id: number,
  status: string,
): Promise<Order> => {
  const { data } = await api.patch<Order>(`/api/v1/orders/${id}/status`, {
    status,
  });
  return data;
};

export const cancelOrder = async (id: number): Promise<Order> => {
  const { data } = await api.post<Order>(`/api/v1/orders/${id}/cancellation`);
  return data;
};

export const listProducts = async (
  params: { search?: string; category_id?: number; page?: number; page_size?: number } = {},
): Promise<ProductPage> => {
  const { data } = await api.get<ProductPage>("/api/v1/products", { params });
  return data;
};

export const getCart = async (): Promise<Cart> => {
  const { data } = await api.get<Cart>("/api/v1/cart");
  return data;
};

export const addCartItem = async (
  product_id: number,
  quantity = 1,
): Promise<Cart> => {
  const { data } = await api.post<Cart>("/api/v1/cart/items", {
    product_id,
    quantity,
  });
  return data;
};

export const updateCartItem = async (
  item_id: number,
  quantity: number,
): Promise<Cart> => {
  const { data } = await api.patch<Cart>(`/api/v1/cart/items/${item_id}`, {
    quantity,
  });
  return data;
};

export const removeCartItem = async (item_id: number): Promise<Cart> => {
  const { data } = await api.delete<Cart>(`/api/v1/cart/items/${item_id}`);
  return data;
};

export const checkout = async (
  address: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
  },
  idempotencyKey: string,
): Promise<Order> => {
  const { data } = await api.post<Order>(
    "/api/v1/orders",
    { address },
    { headers: { "Idempotency-Key": idempotencyKey } },
  );
  return data;
};

export const attemptPayment = async (
  orderId: number,
  outcome = "success",
): Promise<Payment> => {
  const { data } = await api.post<Payment>(
    `/api/v1/payments/${orderId}/attempt`,
    { outcome },
    { headers: { "Idempotency-Key": `payment-${orderId}-${Date.now()}` } },
  );
  return data;
};

// ─── Add Your Custom API Functions Below ─────────────────────────────────────
// Add your application-specific API functions here
// Example:
//
// export const listYourModels = async (): Promise<YourModel[]> => {
//   const { data } = await api.get<YourModel[]>('/your-endpoint')
//   return data
// }
//
// export const createYourModel = async (payload: YourModelCreate): Promise<YourModel> => {
//   const { data } = await api.post<YourModel>('/your-endpoint', payload)
//   return data
// }
