export enum PostStatus {
  READY = "ready",
  SCHEDULED = "scheduled",
  POSTED = "posted",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

// Thêm interface cho channel đơn giản
export interface SimpleChannel {
  id: number;
  platform: string;
  name: string;
}

export interface Post {
  id: number;
  content: string; // Ở frontend gọi là content thay vì caption
  status: PostStatus; // ✅ khớp enum backend
  scheduled_time?: string;
  target_channel_ids: number[];
  created_at: string;
  updated_at?: string;
  media_ids?: number[];
  // Thêm trường channels để hiển thị thông tin
  channels: SimpleChannel[];
}

export interface PostTarget {
  id: number;
  post_id: number;
  channel_id: number;
  status: "ready" | "scheduled" | "posted" | "failed" | "cancelled";
  platform_post_id?: string;
  error_message?: string;
  published_at?: string;
}

export interface PostCreateInput {
  content: string;
  target_channel_ids: number[];
  media_ids?: number[];
  template_id?: number;
  scheduled_time?: string; // ISO string
}

export interface PostUpdateInput {
  content?: string;
  target_channel_ids?: number[];
  media_ids?: number[];
  template_id?: number;
  scheduled_time?: string;
}
