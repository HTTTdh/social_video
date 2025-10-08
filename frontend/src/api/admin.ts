import { apiClient } from "./client";
import type {
  Role,
  User,
  UserCreateInput,
  UserUpdateInput,
} from "@/types/admin";

export const adminApi = {
  // ===== ROLES =====
  listRoles: async (): Promise<Role[]> => {
    const response = await apiClient.get<Role[]>("/admin/roles");
    return response.data;
  },

  createRole: async (data: {
    name: string;
    permissions?: Record<string, any>;
  }): Promise<Role> => {
    const response = await apiClient.post<Role>("/admin/roles", data);
    return response.data;
  },

  updateRole: async (
    id: number,
    data: { name?: string; permissions?: Record<string, any> }
  ): Promise<Role> => {
    const response = await apiClient.patch<Role>(`/admin/roles/${id}`, data);
    return response.data;
  },

  deleteRole: async (id: number): Promise<void> => {
    await apiClient.delete(`/admin/roles/${id}`);
  },

  // ===== USERS =====
  listUsers: async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>("/admin/users");
    return response.data;
  },

  createUser: async (data: UserCreateInput): Promise<User> => {
    const response = await apiClient.post<User>("/admin/users", data);
    return response.data;
  },

  updateUser: async (id: number, data: UserUpdateInput): Promise<User> => {
    const response = await apiClient.patch<User>(`/admin/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await apiClient.delete(`/admin/users/${id}`);
  },

  exportUsers: async (): Promise<Blob> => {
    const response = await apiClient.get("/admin/users/export", {
      responseType: "blob",
    });
    return response.data;
  },
};
