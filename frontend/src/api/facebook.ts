import { apiClient } from "./client";

export const facebookApi = {
  listChannels: async (): Promise<any[]> => {
    const response = await apiClient.get("/facebook/channels");
    return response.data;
  },

  // ✅ Đổi tên: createTextPost
  createTextPost: async (
    channelId: number,
    data: {
      message: string;
      link?: string;
      schedule_unix?: number;
    }
  ) => {
    const response = await apiClient.post(
      `/facebook/channels/${channelId}/post-feed`,
      data
    );
    return response.data;
  },

  // ✅ Đổi tên: createPhotoPost
  createPhotoPost: async (
    channelId: number,
    data: {
      image_urls: string[];
      message: string;
      schedule_unix?: number;
    }
  ) => {
    const response = await apiClient.post(
      `/facebook/channels/${channelId}/post-photos`,
      data
    );
    return response.data;
  },

  // ✅ Đổi tên: createVideoPost
  createVideoPost: async (
    channelId: number,
    data: {
      video_url: string;
      title: string;
      description?: string;
    }
  ) => {
    const response = await apiClient.post(
      `/facebook/channels/${channelId}/post-video`,
      data
    );
    return response.data;
  },
};
