import { useState } from "react";
import { oauthApi, Platform } from "@/api/oauth";

export const useOAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = async (platform: Platform): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const success = await oauthApi.openOAuthPopup(platform);
      return success;
    } catch (err: any) {
      const message = err.message || `Failed to connect ${platform}`;
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { connect, loading, error };
};
