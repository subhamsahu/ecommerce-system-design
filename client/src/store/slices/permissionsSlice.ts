import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { getRolePermissions, updateRolePermissions } from "@/api/client";
import type { RolePermissionsMap, PermissionSet } from "@/types";

const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail || "Failed to save permissions";

// ── Default fallback (used before API loads) ──────────────────────────────────

export const DEFAULT_ROLE_PERMISSIONS: RolePermissionsMap = {
  admin: {
    canViewDashboard: true,
    canViewUserManagement: true,
    canManageUsers: true,
    canViewSettings: true,
    // Add your custom permissions here
  },
  staff: {
    canViewDashboard: true,
    canViewUserManagement: false,
    canManageUsers: false,
    canViewSettings: true,
    // Add your custom permissions here
  },
  employee: {
    canViewDashboard: true,
    canViewUserManagement: false,
    canManageUsers: false,
    canViewSettings: true,
    // Add your custom permissions here
  },
};

// ── State ─────────────────────────────────────────────────────────────────────

interface PermissionsState {
  rolePermissions: RolePermissionsMap;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

const initialState: PermissionsState = {
  rolePermissions: DEFAULT_ROLE_PERMISSIONS,
  isLoading: false,
  isSaving: false,
  error: null,
};

// ── Thunks ────────────────────────────────────────────────────────────────────

export const loadRolePermissions = createAsyncThunk(
  "permissions/load",
  async (_, { rejectWithValue }) => {
    try {
      return await getRolePermissions();
    } catch {
      return rejectWithValue("Failed to load permissions");
    }
  },
);

export const saveRolePermissions = createAsyncThunk(
  "permissions/save",
  async (
    { role, permissions }: { role: string; permissions: PermissionSet },
    { rejectWithValue },
  ) => {
    try {
      const updated = await updateRolePermissions(role, permissions);
      return { role, permissions: updated };
    } catch (error) {
      return rejectWithValue(errorMessage(error));
    }
  },
);

// ── Slice ─────────────────────────────────────────────────────────────────────

const permissionsSlice = createSlice({
  name: "permissions",
  initialState,
  reducers: {
    clearPermissionsError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadRolePermissions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadRolePermissions.fulfilled, (state, action) => {
        state.isLoading = false;
        // Merge API result over defaults (admin stays hardcoded)
        state.rolePermissions = {
          ...DEFAULT_ROLE_PERMISSIONS,
          ...action.payload,
        };
      })
      .addCase(loadRolePermissions.rejected, (state) => {
        state.isLoading = false;
        // Keep fallback defaults on error
      });

    builder
      .addCase(saveRolePermissions.pending, (state) => {
        state.isSaving = true;
        state.error = null;
      })
      .addCase(saveRolePermissions.fulfilled, (state, action) => {
        state.isSaving = false;
        state.rolePermissions[action.payload.role] = action.payload.permissions;
      })
      .addCase(saveRolePermissions.rejected, (state, action) => {
        state.isSaving = false;
        state.error = String(action.payload ?? "Failed to save");
      });
  },
});

export const { clearPermissionsError } = permissionsSlice.actions;
export default permissionsSlice.reducer;
