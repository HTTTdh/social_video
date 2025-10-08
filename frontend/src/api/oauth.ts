import { apiClient } from "./client";
import type { Platform } from "@/types/channel";
import { ENV } from "@/config/env";

export const oauthApi = {
  // Mở popup tới backend /oauth/{provider}/start
  startOAuth: (
    provider: "facebook" | "instagram" | "tiktok" | "youtube"
  ): Window | null => {
    const width = 600;
    const height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;

    // Đảm bảo không bị double slash, và có /api nếu API_BASE_URL đã bao gồm
    const apiBase = ENV.API_BASE_URL.replace(/\/+$/, "");
    const url = `${apiBase}/oauth/${provider}/start`;

    return window.open(
      url,
      `oauth-${provider}`,
      `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );
  },

  // Lắng nghe message từ popup callback (tuỳ chọn, không bắt buộc nếu dùng openOAuthPopup)
  handleCallback: (): Promise<{ provider: string; success: boolean }> =>
    new Promise((resolve) => {
      const handler = (event: MessageEvent) => {
        // Chỉ chấp nhận message từ backend origin
        const backendOrigin = new URL(ENV.API_BASE_URL).origin;
        if (event.origin !== backendOrigin) return;

        if (event.data?.provider && typeof event.data.success === "boolean") {
          window.removeEventListener("message", handler);
          resolve(event.data);
        }
      };
      window.addEventListener("message", handler);
    }),

  // API tiện dụng để mở popup và chờ kết quả
  openOAuthPopup: (platform: Platform): Promise<boolean> =>
    new Promise((resolve, reject) => {
      try {
        // ❗ Không await startOAuth, không destructure authorize_url
        const popup = oauthApi.startOAuth(platform);
        if (!popup) {
          reject(new Error("Popup blocked. Please allow popups."));
          return;
        }

        const backendOrigin = new URL(ENV.API_BASE_URL).origin;

        const handleMessage = (event: MessageEvent) => {
          if (event.origin !== backendOrigin) return;

          if (
            event.data?.type === "oauth-success" &&
            event.data?.platform === platform
          ) {
            window.removeEventListener("message", handleMessage);
            clearInterval(checkClosed);
            try {
              popup.close();
            } catch {}
            resolve(true);
          } else if (event.data?.type === "oauth-error") {
            window.removeEventListener("message", handleMessage);
            clearInterval(checkClosed);
            try {
              popup.close();
            } catch {}
            reject(new Error(event.data.message || "OAuth failed"));
          }
        };

        window.addEventListener("message", handleMessage);

        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            window.removeEventListener("message", handleMessage);
            reject(new Error("OAuth cancelled by user"));
          }
        }, 500);
      } catch (error) {
        reject(error as Error);
      }
    }),
};
