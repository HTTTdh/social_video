import { apiClient } from "./client";
import type {
  Channel,
  ChannelCreateInput,
  ChannelUpdateInput,
  ChannelTokenInput,
} from "@/types/channel";

export const channelsApi = {
  list: async (params?: {
    platform?: string;
    only_active?: boolean;
  }): Promise<Channel[]> => {
    const response = await apiClient.get<Channel[]>("/channels", {
      params,
    });
    return response.data;
  },

  getById: async (id: number): Promise<Channel> => {
    const response = await apiClient.get<Channel>(`/channels/${id}`);
    return response.data;
  },

  create: async (data: ChannelCreateInput): Promise<Channel> => {
    const response = await apiClient.post<Channel>("/channels", data);
    return response.data;
  },

  update: async (id: number, data: ChannelUpdateInput): Promise<Channel> => {
    const response = await apiClient.patch<Channel>(`/channels/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/channels/${id}`);
  },

  setManualToken: async (
    channelId: number,
    data: ChannelTokenInput
  ): Promise<void> => {
    await apiClient.post(`/channels/${channelId}/token`, data);
  },
};
