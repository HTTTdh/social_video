export interface Role {
  id: number;
  name: string;
  permissions: Record<string, any>;
}

export interface BaseUser {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
