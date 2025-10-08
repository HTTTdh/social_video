import { apiClient } from "./client";
import type {
  Schedule,
  ScheduleCreateInput,
  ScheduleUpdateInput,
} from "@/types/schedule";

export const scheduleApi = {
  list: async (): Promise<Schedule[]> => {
    const response = await apiClient.get<Schedule[]>("/schedules"); // ✅ /schedules
    return response.data;
  },

  getById: async (id: number): Promise<Schedule> => {
    const response = await apiClient.get<Schedule>(`/schedules/${id}`);
    return response.data;
  },

  create: async (data: ScheduleCreateInput): Promise<Schedule> => {
    const response = await apiClient.post<Schedule>("/schedules", data);
    return response.data;
  },

  update: async (id: number, data: ScheduleUpdateInput): Promise<Schedule> => {
    const response = await apiClient.patch<Schedule>(`/schedules/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/schedules/${id}`);
  },

  getCalendar: async (params?: {
    start?: string;
    end?: string;
  }): Promise<any[]> => {
    const response = await apiClient.get("/schedules/calendar", { params }); // ✅ /schedules
    return response.data;
  },

  execute: async (id: number): Promise<void> => {
    await apiClient.post(`/schedules/${id}/execute`);
  },
};
