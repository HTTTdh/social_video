export enum MediaType {
  IMAGE = "image",
  VIDEO = "video",
  AUDIO = "audio",
}

export interface MediaAsset {
  id: number;
  title: string;
  type: MediaType;
  url: string;
  mime_type: string;
  size?: number;
  alt_text?: string;
  created_at?: string;
  updated_at?: string;
}

export interface MediaUploadData {
  file: File;
  title?: string;
  alt_text?: string;
}
