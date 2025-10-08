export const ENV = {
  API_BASE_URL:
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  APP_NAME: import.meta.env.VITE_APP_NAME || "VideoV02",
} as const;
