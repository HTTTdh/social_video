import { apiClient } from "./client";

export const tiktokApi = {
  listChannels: async () => {
    const response = await apiClient.get("/tiktok/channels");
    return response.data;
  },

  uploadVideo: async (
    channelId: number,
    data: {
      video_path: string;
      caption: string;
      privacy_level?: "PUBLIC" | "PRIVATE" | "FOLLOWERS";
    }
  ) => {
    const response = await apiClient.post(
      `/tiktok/channels/${channelId}/upload`,
      data
    );
    return response.data;
  },
};
