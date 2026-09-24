/* ---------------------------------------------------
 * Shared TypeScript types mirroring server schemas.
 * ------------------------------------------------- */

// ── Auth ─────────────────────────────────────────────

export interface UserResponse {
  id: number;
  username: string;
  email?: string | null;
  full_name?: string | null;
  role: string;
  is_active?: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// ── Permissions ──────────────────────────────────────

export interface RolePermissions {
  id: number;
  role: string;
  permissions: Record<string, boolean>;
  updated_at: string;
}

export interface PermissionSet {
  canViewDashboard: boolean;
  canViewUserManagement: boolean;
  canManageUsers: boolean;
  canViewSettings: boolean;
  // Add your custom permissions here
}

/** Map of role name → its PermissionSet (only staff + employee are returned) */
export type RolePermissionsMap = Record<string, PermissionSet>;

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string | null;
  price: number | string;
  currency: string;
  category_id?: number | null;
  is_published: boolean;
  is_archived: boolean;
  available_quantity?: number;
  created_at: string;
  updated_at?: string | null;
}

export interface ProductPayload {
  name: string;
  sku: string;
  description?: string;
  price: number;
  currency: string;
  category_id?: number | null;
}

export interface ProductUpdatePayload {
  name?: string;
  description?: string;
  price?: number;
  category_id?: number | null;
  is_published?: boolean;
  is_archived?: boolean;
}

export interface InventoryRecord {
  product_id: number;
  quantity: number;
  low_stock_threshold: number;
}

export interface OrderItem {
  product_name: string;
  sku: string;
  quantity: number;
  unit_price: number | string;
}

export interface Order {
  id: number;
  status: string;
  currency: string;
  total: number | string;
  created_at: string;
  items: OrderItem[];
}

export interface ProductPage {
  items: Product[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
}

export interface OrderPage {
  items: Order[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
}

export interface CartItem {
  id: number;
  product_id: number;
  name: string;
  sku: string;
  quantity: number;
  unit_price: number | string;
  available_quantity: number;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total: number | string;
}

export interface Payment {
  id: number;
  order_id: number;
  status: string;
  amount: number | string;
}

// ─── Add Your Custom Types Below ─────────────────────
// Add your application-specific TypeScript interfaces here
// Example:
// export interface YourModel {
//   id: number
//   name: string
//   created_at: string
// }
