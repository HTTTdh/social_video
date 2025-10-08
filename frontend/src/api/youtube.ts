import { apiClient } from "./client";

export const youtubeApi = {
  listChannels: async () => {
    const response = await apiClient.get("/youtube/channels");
    return response.data;
  },

  uploadVideo: async (
    channelId: number,
    data: {
      video_path?: string;
      video_url?: string;
      title: string;
      description?: string;
      tags?: string[];
      privacy_status?: "public" | "private" | "unlisted";
      schedule_time_iso?: string;
    }
  ) => {
    const response = await apiClient.post(
      `/youtube/channels/${channelId}/upload`,
      data
    );
    return response.data;
  },
};
