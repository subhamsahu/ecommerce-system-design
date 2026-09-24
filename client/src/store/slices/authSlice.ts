import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { loginUser as apiLogin } from "@/api/client";
import type { UserResponse } from "@/types";

const errorMessage = (error: unknown) =>
  (error as { response?: { data?: { detail?: string } } })?.response?.data
    ?.detail || "Login failed";

// Initial state
const storedUser = (() => {
  try {
    const u = localStorage.getItem("user");
    return u ? (JSON.parse(u) as UserResponse) : null;
  } catch {
    return null;
  }
})();

const initialState = {
  user: storedUser as UserResponse | null,
  token: localStorage.getItem("token"),
  isLoading: false,
  error: null as string | null,
  isAuthenticated: !!localStorage.getItem("token"),
};

// Login thunk — calls finance backend with username + password
export const loginUser = createAsyncThunk(
  "auth/loginUser",
  async (
    credentials: { username: string; password: string },
    { rejectWithValue },
  ) => {
    try {
      const data = await apiLogin(credentials.username, credentials.password);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      return { token: data.access_token, user: data.user };
    } catch (error) {
      return rejectWithValue(errorMessage(error));
    }
  },
);

export const logoutUser = createAsyncThunk("auth/logoutUser", async () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  return null;
});

// Auth slice
const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.isAuthenticated = true;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = String(action.payload || "Login failed");
      });

    // Logout
    builder.addCase(logoutUser.fulfilled, (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
    });
  },
});

export const { clearError, logout } = authSlice.actions;
export default authSlice.reducer;
