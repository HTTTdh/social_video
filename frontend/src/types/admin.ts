import type { BaseUser, Role } from "./common";

export interface User extends BaseUser {
  roles: Role[];
}

export interface UserCreateInput {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role_ids: number[];
  is_active: boolean;
}

export interface UserUpdateInput {
  full_name?: string;
  role_ids?: number[];
  is_active?: boolean;
}

export type { Role } from "./common";
