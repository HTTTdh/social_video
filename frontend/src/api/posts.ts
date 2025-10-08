import { apiClient } from "./client";
import type { Post, PostCreateInput, PostUpdateInput } from "@/types/post";
import { PostStatus } from "@/types/post";

// FE -> BE
const adaptPostToBackend = (data: PostCreateInput) => ({
  caption: data.content,
  targets: (data.target_channel_ids || []).map((id) => ({ channel_id: id })),
  default_scheduled_time: data.scheduled_time, // BE dùng default_scheduled_time
  // media_ids/template_id nếu BE không định nghĩa sẽ bị bỏ qua (Pydantic extra=ignore)
  media_ids: data.media_ids,
  template_id: data.template_id,
});

// BE -> FE
const adaptPostFromBackend = (post: any): Post => {
  const targets = Array.isArray(post.targets) ? post.targets : [];
  // Lấy giờ hẹn sớm nhất từ targets (BE không lưu default_scheduled_time trên post)
  const firstSchedule = targets
    .map((t: any) => t.scheduled_time)
    .filter(Boolean)
    .sort()[0];

  return {
    id: post.id,
    content: post.caption || "",
    status: (post.status as PostStatus) ?? PostStatus.READY,
    scheduled_time: firstSchedule,
    target_channel_ids: targets.map((t: any) => t.channel_id),
    created_at: post.created_at,
    updated_at: post.updated_at,
    media_ids: post.media_ids || [],
    channels: targets.map((t: any) => ({
      id: t.channel_id,
      platform: t.platform || t?.channel?.platform || "unknown",
      name: t?.channel?.name || "Unknown Channel",
    })),
  };
};

const normalizeListResponse = (data: any): { items: Post[]; total: number } => {
  const rawItems = Array.isArray(data)
    ? data
    : Array.isArray(data?.items)
    ? data.items
    : [];
  const items = rawItems.map(adaptPostFromBackend);
  const total = Array.isArray(data)
    ? items.length
    : data?.total ?? items.length;
  return { items, total };
};

const adaptStatusFilter = (s?: string) => {
  if (!s) return undefined;
  if (s === "published") return "posted";
  if (s === "draft") return "ready";
  return s;
};

export const postsApi = {
  list: async (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ items: Post[]; total: number }> => {
    const res = await apiClient.get("/posts", {
      params: { ...params, status: adaptStatusFilter(params?.status) },
    });
    return normalizeListResponse(res.data);
  },

  getById: async (id: number): Promise<Post> => {
    const res = await apiClient.get(`/posts/${id}`);
    return adaptPostFromBackend(res.data);
  },

  create: async (data: PostCreateInput): Promise<Post> => {
    const res = await apiClient.post("/posts", adaptPostToBackend(data));
    return adaptPostFromBackend(res.data);
  },

  update: async (id: number, data: PostUpdateInput): Promise<Post> => {
    const res = await apiClient.put(
      `/posts/${id}`,
      adaptPostToBackend(data as PostCreateInput)
    );
    return adaptPostFromBackend(res.data);
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/posts/${id}`);
  },

  publishNow: async (id: number): Promise<void> => {
    await apiClient.post(`/posts/${id}/publish`);
  },
};
