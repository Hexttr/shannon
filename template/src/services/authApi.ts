import api from './api';
import { LoginRequest, Token, User } from '../types';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<{ data: Token }> => {
    const response = await api.post<Token>('/api/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    return response;
  },

  logout: () => {
    localStorage.removeItem('access_token');
  },

  getMe: async (): Promise<{ data: User }> => {
    return api.get<User>('/api/auth/me');
  },
};


