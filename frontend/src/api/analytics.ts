import { apiClient } from "./client";
import type {
  AnalyticsData,
  ChannelStats,
  DashboardStats,
} from "@/types/analytics";

export const analyticsApi = {
  getDashboard: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>(
      "/analytics/dashboard"
    );
    return response.data;
  },

  getChannelStats: async (channelId: number): Promise<ChannelStats> => {
    const response = await apiClient.get<ChannelStats>(
      `/analytics/channels/${channelId}`
    );
    return response.data;
  },

  getTimeSeries: async (params: {
    channel_id?: number;
    start_date: string;
    end_date: string;
  }): Promise<AnalyticsData[]> => {
    const response = await apiClient.get<AnalyticsData[]>(
      "/analytics/time-series",
      { params }
    );
    return response.data;
  },
};
