import { apiClient } from "./client";

export const instagramApi = {
  listChannels: async (params?: {
    q?: string;
    only_active?: boolean;
  }): Promise<any[]> => {
    const response = await apiClient.get("/instagram/channels", { params });
    return response.data;
  },

  // ✅ Đổi tên: createPhotoPost (nhất quán với Facebook)
  createPhotoPost: async (
    channelId: number,
    data: {
      image_url: string;
      caption?: string;
    }
  ) => {
    const response = await apiClient.post(
      `/instagram/channels/${channelId}/post-photo`,
      data
    );
    return response.data;
  },

  // ✅ Đổi tên: createVideoPost
  createVideoPost: async (
    channelId: number,
    data: {
      video_url: string;
      caption?: string;
      is_reel?: boolean;
    }
  ) => {
    const response = await apiClient.post(
      `/instagram/channels/${channelId}/post-video`,
      data
    );
    return response.data;
  },

  // ✅ Đổi tên: createCarouselPost
  createCarouselPost: async (
    channelId: number,
    data: {
      media_urls: string[];
      caption?: string;
    }
  ) => {
    const response = await apiClient.post(
      `/instagram/channels/${channelId}/post-carousel`,
      data
    );
    return response.data;
  },
};
