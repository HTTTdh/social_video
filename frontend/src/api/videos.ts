import { apiClient } from "./client";
import type {
  Video,
  VideoStatus,
  TrimVideoInput,
  WatermarkInput,
  ThumbnailInput,
} from "@/types/video";

// ĐỔI TẠI ĐÂY nếu backend của bạn không có /api prefix
const BASE = "/videos"; // hoặc "/api/videos" nếu bạn thực sự mount như vậy

export const videosApi = {
  // Backend trả về mảng Video[] — SỬA LẠI CHO KHỚP
  list: async (params?: {
    status?: VideoStatus;
    limit?: number;
    offset?: number;
  }): Promise<Video[]> => {
    const res = await apiClient.get<Video[]>(`${BASE}`, { params });
    return res.data;
  },

  getById: async (id: number): Promise<Video> => {
    const res = await apiClient.get<Video>(`${BASE}/${id}`);
    return res.data;
  },

  // ✅ nhận File | File[]
  upload: async (
    fileOrFiles: File | File[],
    metadata?: { title?: string; description?: string; channel_id?: number },
    onProgress?: (progress: number) => void
  ): Promise<Video[]> => {
    const files = Array.isArray(fileOrFiles) ? fileOrFiles : [fileOrFiles];
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f)); // ✅ key "files"
    if (metadata?.title) formData.append("title", metadata.title);
    if (metadata?.channel_id != null)
      formData.append("channel_id", String(metadata.channel_id));
    // description hiện backend không nhận => có thể bỏ qua

    const res = await apiClient.post<Video[]>(`${BASE}/upload`, formData, {
      onUploadProgress: (e) => {
        if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total));
      },
    });
    return res.data;
  },

  // Backend có PUT (không phải PATCH)
  update: async (
    id: number,
    data: { title?: string; description?: string }
  ): Promise<Video> => {
    const res = await apiClient.put<Video>(`${BASE}/${id}`, data);
    return res.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`${BASE}/${id}`);
  },

  trim: async (data: TrimVideoInput): Promise<Video> => {
    const res = await apiClient.post<Video>(`${BASE}/trim`, data);
    return res.data;
  },

  addWatermark: async (data: WatermarkInput): Promise<Video> => {
    const res = await apiClient.post<Video>(`${BASE}/watermark`, data);
    return res.data;
  },

  // ✅ đúng endpoint backend
  generateThumbnail: async (data: ThumbnailInput): Promise<Video> => {
    const res = await apiClient.post<Video>(`${BASE}/thumbnail/auto`, data);
    return res.data;
  },

  // ⚠️ Backend chưa có route này -> sẽ 404
  download: async (id: number): Promise<Blob> => {
    const res = await apiClient.get(`${BASE}/${id}/download`, {
      responseType: "blob",
    });
    return res.data;
  },
};
