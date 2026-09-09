import apiClient from './client';
import type { User, LoginRequest, RegisterRequest, LoginResponse } from '../../types/auth';

export const authApi = {
  // 登录
  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>('/auth/login', data),

  // 注册
  register: (data: RegisterRequest) =>
    apiClient.post<{ data: User }>('/auth/register', data),

  // 获取当前用户信息
  me: () => apiClient.get<{ data: User }>('/auth/me'),

  // 登出
  logout: () => apiClient.post('/auth/logout'),
};
