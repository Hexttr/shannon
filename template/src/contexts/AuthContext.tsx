import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../services/authApi';
import { User } from '../types';

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
    // Проверяем токен при загрузке
    window.__DEBUG__?.log('[AuthContext] Проверка токена при загрузке...');
    const token = localStorage.getItem('access_token');
    if (token) {
      window.__DEBUG__?.log('[AuthContext] Токен найден, проверяем авторизацию...');
      checkAuth();
    } else {
      window.__DEBUG__?.log('[AuthContext] Токен не найден, устанавливаем isLoading=false');
      setIsLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      window.__DEBUG__?.log('[AuthContext] Выполняем checkAuth...');
      const response = await authApi.getMe();
      window.__DEBUG__?.log('[AuthContext] getMe успешно:', response.data);
      setUser(response.data);
    } catch (error: any) {
      window.__DEBUG__?.log('[AuthContext] Ошибка checkAuth:', error?.message || error);
      localStorage.removeItem('access_token');
      setUser(null);
    } finally {
      window.__DEBUG__?.log('[AuthContext] Устанавливаем isLoading=false');
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      await authApi.login({ username, password });
      await checkAuth();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Ошибка входа');
    }
  };

  const logout = () => {
    authApi.logout();
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


