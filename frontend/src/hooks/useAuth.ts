import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/api/auth";
import { LoginRequest } from "@/types/auth";

export const useAuth = () => {
  const { user, isAuthenticated, setAuth, setUser, clearAuth } = useAuthStore();

  const login = async (credentials: LoginRequest) => {
    const response = await authApi.login(credentials);
    const userData = await authApi.getMe();
    setAuth(userData, response.access_token, response.refresh_token);
    return userData;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      clearAuth();
    }
  };

  const loadUser = async () => {
    if (!isAuthenticated) return;
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      clearAuth();
    }
  };

  return { user, isAuthenticated, login, logout, loadUser };
};
