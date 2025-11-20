import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Проверяем сохраненного пользователя при загрузке
    const checkAuth = async () => {
      try {
        if (authApi.isAuthenticated()) {
          try {
            const currentUser = await authApi.getCurrentUser();
            setUser(currentUser);
          } catch (error: any) {
            // Токен невалиден или сервер не отвечает
            console.warn('Не удалось проверить токен:', error.message);
            // Если это ошибка сети (не 401), сохраняем пользователя из localStorage
            if (error.code === 'ECONNABORTED' || !error.response) {
              // Сервер не отвечает, используем сохраненного пользователя
              const storedUser = authApi.getStoredUser();
              if (storedUser) {
                setUser(storedUser);
              }
            } else {
              // Токен невалиден, очищаем
              authApi.logout();
            }
          }
        } else {
          // Если нет токена, пытаемся восстановить пользователя из localStorage
          const storedUser = authApi.getStoredUser();
          if (storedUser) {
            setUser(storedUser);
          }
        }
      } catch (error) {
        console.error('Ошибка проверки аутентификации:', error);
        authApi.logout();
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login({ username, password });
      setUser(response.user);
    } catch (error: any) {
      // Пробрасываем ошибку дальше для обработки в компоненте
      throw error;
    }
  };

  const register = async (username: string, email: string, password: string) => {
    await authApi.register({ username, email, password });
    // После регистрации автоматически входим
    await login(username, password);
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      if (authApi.isAuthenticated()) {
        const currentUser = await authApi.getCurrentUser();
        setUser(currentUser);
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isAdmin: user?.is_admin || false,
        login,
        register,
        logout,
        refreshUser,
        loading,
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

