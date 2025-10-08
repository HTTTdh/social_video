export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  DASHBOARD: "/dashboard",
  CHANNELS: "/channels",
  OAUTH_CALLBACK: "/oauth/:platform/callback",
  POSTS: "/posts",
  POST_CREATE: "/posts/create",
  POST_DETAIL: "/posts/:id",
  MEDIA: "/media",
  ANALYTICS: "/analytics",
} as const;
