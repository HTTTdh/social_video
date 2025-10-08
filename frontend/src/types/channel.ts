export enum Platform {
  FACEBOOK = "facebook",
  INSTAGRAM = "instagram",
  TIKTOK = "tiktok",
  YOUTUBE = "youtube",
}

export interface Channel {
  id: number;
  platform: Platform;
  name: string;
  username?: string;
  external_id: string;
  avatar_url?: string;
  access_token?: string;
  refresh_token?: string;
  token_expires_at?: string;
  is_active: boolean;
  channel_metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface ChannelCreateInput {
  platform: Platform;
  name: string;
  external_id: string;
  username?: string;
  is_active?: boolean;
  metadata?: Record<string, any>;
}

export interface ChannelUpdateInput {
  name?: string;
  username?: string;
  is_active?: boolean;
  metadata?: Record<string, any>;
}

export interface ChannelTokenInput {
  platform: Platform;
  access_token: string;
  refresh_token?: string;
  external_id?: string;
  token_expires_at?: string;
}
