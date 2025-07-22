export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'requester' | 'sublead' | 'executive' | 'business';
  is_active: boolean;
  email_verified: boolean;
  last_login?: string;
  login_count: number;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  password: string;
}
