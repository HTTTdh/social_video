import { apiClient } from "./client";
import { MediaAsset, MediaType } from "@/types/media";

const API_BASE = apiClient.defaults.baseURL || "";
const API_ROOT = API_BASE.replace(/\/api\/?$/, "");

const normalizePath = (p?: string) =>
  (p || "").replace(/\\/g, "/").replace(/^\/+/, "");

const mapBackendToFrontend = (backendAsset: any): MediaAsset => {
  const path = normalizePath(backendAsset.path);
  return {
    id: backendAsset.id,
    title:
      backendAsset.title ||
      backendAsset.path
        ?.split(/[\\/]/)
        .pop()
        ?.replace(/\.[^/.]+$/, "") ||
      "Untitled",
    type: backendAsset.type as MediaType,
    url: `${API_ROOT}/${path}`,
    mime_type: backendAsset.mime_type || "",
    size: backendAsset.size,
    alt_text:
      backendAsset.metadata?.alt_text || backendAsset.media_metadata?.alt_text,
    created_at: backendAsset.created_at,
    updated_at: backendAsset.updated_at,
  };
};

export const mediaApi = {
  list: async (params?: {
    type?: MediaType | string;
    time_filter?: string;
    q?: string;
    mime?: string;
    limit?: number;
    offset?: number;
  }) => {
    const response = await apiClient.get<any[]>("/media", {
      params: {
        type_filter: params?.type,
        time_filter: params?.time_filter,
        q: params?.q,
      },
    });
    const items = (response.data || []).map(mapBackendToFrontend);
    return { items, total: items.length };
  },

  getStats: async () => (await apiClient.get("/media/stats")).data,

  upload: async (
    file: File,
    metadata?: Record<string, any>,
    onProgress?: (p: number) => void
  ) => {
    const formData = new FormData();
    formData.append("files", file);
    if (metadata)
      Object.entries(metadata).forEach(([k, v]) =>
        formData.append(k, typeof v === "string" ? v : JSON.stringify(v))
      );

    // ⚠️ baseURL đã có /api → endpoint chỉ là "/media/upload"
    const response = await apiClient.post<any[]>("/media/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total));
      },
    });

    return mapBackendToFrontend(response.data[0]);
  },

  getById: async (id: number) =>
    mapBackendToFrontend((await apiClient.get<any>(`/media/${id}`)).data),
  update: async (id: number, data: Record<string, any>) =>
    mapBackendToFrontend((await apiClient.put<any>(`/media/${id}`, data)).data),
  delete: async (id: number) => {
    await apiClient.delete(`/media/${id}`);
  },
};
