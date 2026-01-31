import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../services/authApi';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    window.__DEBUG__?.log('[AuthContext] Проверка токена при загрузке...');
    const token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user');
    window.__DEBUG__?.log('[AuthContext] Токен в localStorage:', token ? 'найден' : 'не найден');
    window.__DEBUG__?.log('[AuthContext] Пользователь в localStorage:', savedUser ? 'найден' : 'не найден');

    if (token && savedUser) {
      try {
        window.__DEBUG__?.log('[AuthContext] Проверка токена через API...');
        const response = await authApi.getMe();
        window.__DEBUG__?.log('[AuthContext] Токен валиден, пользователь:', response.data);
        setUser(response.data);
      } catch (error: any) {
        window.__DEBUG__?.log('[AuthContext] Токен невалиден:', error.response?.status, error.response?.data);
        // Токен невалиден, очищаем
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setUser(null);
      }
    } else {
      window.__DEBUG__?.log('[AuthContext] Токен не найден, устанавливаем isLoading=false');
    }
    setIsLoading(false);
  };

  const login = async (username: string, password: string) => {
    try {
      window.__DEBUG__?.log('[AuthContext] Попытка входа:', username);
      const response = await authApi.login({ username, password });
      window.__DEBUG__?.log('[AuthContext] Ответ от API:', response);
      
      const { user: userData, token } = response.data;
      window.__DEBUG__?.log('[AuthContext] Токен получен:', token ? 'да' : 'нет');
      window.__DEBUG__?.log('[AuthContext] Пользователь получен:', userData);

      localStorage.setItem('auth_token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      window.__DEBUG__?.log('[AuthContext] Данные сохранены в localStorage');
    } catch (error: any) {
      window.__DEBUG__?.log('[AuthContext] Ошибка входа:', error);
      window.__DEBUG__?.log('[AuthContext] Ответ ошибки:', error.response?.data);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

