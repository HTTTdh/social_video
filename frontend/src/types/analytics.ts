export interface AnalyticsData {
  date: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
}

export interface ChannelStats {
  channel_id: number;
  channel_name: string;
  platform: string;
  total_posts: number;
  total_views: number;
  engagement_rate: number;
}

export interface DashboardStats {
  total_posts: number;
  total_channels: number;
  total_scheduled: number;
  engagement_rate: number;
  trending_posts: any[];
}
