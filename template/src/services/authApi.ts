import api from './api';
import type { User } from '../types';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
}

export const authApi = {
  login: async (data: LoginRequest) => {
    const response = await api.post<LoginResponse>('/auth/login', data);
    return response;
  },

  getMe: async () => {
    const response = await api.get<User>('/auth/me');
    return response;
  },
};

