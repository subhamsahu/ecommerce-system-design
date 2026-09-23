import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from "react-router-dom";
import Layout from "@/layout/layout";
import LoginPage from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Settings from "@/pages/Settings";
import UserManagement from "@/pages/UserManagement";
import Forbidden from "@/pages/Forbidden";
import NotFound from "@/pages/NotFound";
import ProtectedRoute from "@/components/ProtectedRoute";
import Permissions from "@/pages/Permissions";
import ProductManagement from "@/pages/ProductManagement";
import CategoryManagement from "@/pages/CategoryManagement";
import InventoryManagement from "@/pages/InventoryManagement";
import OrdersManagement from "@/pages/OrdersManagement";
import Sales from "@/pages/Sales";
import Store from "@/pages/Store";

const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    // Outer shell: must be authenticated
    path: "/",
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute requirePermission="canViewDashboard">
            <Dashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: "settings",
        element: (
          <ProtectedRoute requirePermission="canViewSettings">
            <Settings />
          </ProtectedRoute>
        ),
      },
      {
        path: "store",
        element: <Store />,
      },
      {
        // Strictly admin-only — not configurable via permissions page
        path: "user-management",
        element: (
          <ProtectedRoute requireRole="admin">
            <UserManagement />
          </ProtectedRoute>
        ),
      },
      {
        // Strictly admin-only — not configurable via permissions page
        path: "permissions",
        element: (
          <ProtectedRoute requireRole="admin">
            <Permissions />
          </ProtectedRoute>
        ),
      },
      {
        path: "products",
        element: (
          <ProtectedRoute requireRole="admin">
            <ProductManagement />
          </ProtectedRoute>
        ),
      },
      {
        path: "categories",
        element: (
          <ProtectedRoute requireRole="admin">
            <CategoryManagement />
          </ProtectedRoute>
        ),
      },
      {
        path: "inventory",
        element: (
          <ProtectedRoute requireRole="admin">
            <InventoryManagement />
          </ProtectedRoute>
        ),
      },
      {
        path: "orders",
        element: (
          <ProtectedRoute requireRole="admin">
            <OrdersManagement />
          </ProtectedRoute>
        ),
      },
      {
        path: "sales",
        element: (
          <ProtectedRoute requireRole="admin">
            <Sales />
          </ProtectedRoute>
        ),
      },
      {
        path: "forbidden",
        element: <Forbidden />,
      },
      // Add your custom routes here
      // Example:
      // {
      //   path: 'your-feature',
      //   element: (
      //     <ProtectedRoute requirePermission="canViewYourFeature">
      //       <YourFeaturePage />
      //     </ProtectedRoute>
      //   ),
      // },
      {
        path: "*",
        element: <NotFound />,
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
