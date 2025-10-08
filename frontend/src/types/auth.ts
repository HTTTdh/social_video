import { Role } from "./common";

export interface LoginRequest {
  username: string; // ✅ Đổi từ identifier → username
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  roles: Role[]; // ✅ Dùng Role objects
  is_active: boolean;
}
