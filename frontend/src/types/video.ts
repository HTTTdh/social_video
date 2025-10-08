export enum VideoStatus {
  UPLOADING = "uploading",
  PROCESSING = "processing",
  READY = "ready",
  FAILED = "failed",
}

export interface Video {
  id: number;
  title: string;
  description?: string;
  file_path: string;
  file_size?: number;
  duration?: number;
  resolution?: string;
  format: string;
  thumbnail_path?: string;
  video_metadata?: Record<string, any>;
  status: VideoStatus;
  created_at: string;
  updated_at?: string;
}

export interface VideoUpdateInput {
  title?: string;
  description?: string;
  status?: VideoStatus;
  video_metadata?: Record<string, any>;
}

export interface TrimVideoInput {
  video_id: number;
  start: number;
  end?: number;
  reencode?: boolean;
}

export interface WatermarkInput {
  video_id: number;
  watermark_path: string;
  x: number;
  y: number;
  opacity?: number;
}

export interface ThumbnailInput {
  video_id: number;
  method?: "middle" | "scene";
}
