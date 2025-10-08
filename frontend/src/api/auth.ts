import { apiClient } from "./client";
import type { LoginRequest, LoginResponse, AuthUser } from "@/types/auth";

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    // Chuyển đổi username → identifier cho đúng với backend API
    const requestData = {
      identifier: data.username, // Adapter username → identifier
      password: data.password,
    };

    const response = await apiClient.post<LoginResponse>(
      "/auth/login",
      requestData // Gửi dữ liệu đã được chuyển đổi
    );

    // Lưu token
    localStorage.setItem("access_token", response.data.access_token);
    localStorage.setItem("refresh_token", response.data.refresh_token);

    return response.data;
  },

  getMe: async (): Promise<AuthUser> => {
    const response = await apiClient.get<AuthUser>("/auth/me");
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/auth/logout");
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },
};
