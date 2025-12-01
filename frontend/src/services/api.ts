import axios from 'axios';
import { Dessert, PDFExportSettings, LoginCredentials, RegisterData, AuthResponse, User } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 секунд таймаут для запросов (увеличено для загрузки файлов)
});

// Добавляем токен в запросы
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Для multipart/form-data не переопределяем Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

// Обработка ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истек или невалиден
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      // Не делаем редирект автоматически, чтобы не ломать работу приложения
      // Редирект будет сделан в компонентах при необходимости
    }
    return Promise.reject(error);
  }
);

export const dessertsApi = {
  getAll: async (params?: {
    category?: string;
    search?: string;
    is_active?: boolean;
  }): Promise<Dessert[]> => {
    const response = await api.get<Dessert[]>('/desserts/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Dessert> => {
    const response = await api.get<Dessert>(`/desserts/${id}`);
    return response.data;
  },

  getCategories: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/desserts/categories');
    return response.data;
  },

  create: async (dessert: Omit<Dessert, 'id'>): Promise<Dessert> => {
    const response = await api.post<Dessert>('/desserts/', dessert);
    return response.data;
  },

  update: async (id: number, dessert: Partial<Dessert>): Promise<Dessert> => {
    const response = await api.put<Dessert>(`/desserts/${id}`, dessert);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/desserts/${id}`);
  },
};

export const pdfApi = {
  export: async (settings: PDFExportSettings): Promise<Blob> => {
    const response = await api.post('/pdf/export', settings, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const uploadApi = {
  uploadImage: async (file: File): Promise<{ url: string; filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Не устанавливаем Content-Type вручную, браузер сам установит с boundary
    const response = await api.post<{ url: string; filename: string; original_filename: string }>(
      '/upload/image',
      formData,
      {
        headers: {
          // Убираем Content-Type, чтобы браузер сам установил multipart/form-data с boundary
        },
        timeout: 30000, // 30 секунд для больших файлов
      }
    );
    return { url: response.data.url, filename: response.data.filename };
  },

  deleteImage: async (filename: string): Promise<void> => {
    await api.delete(`/upload/image/${filename}`);
  },
};

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login-json', credentials);
    // Сохраняем токен и пользователя
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  logout: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  getStoredUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  updateEmail: async (email: string): Promise<{ message: string; user: User }> => {
    const response = await api.put<{ message: string; user: User }>('/auth/profile/email', { email });
    // Обновляем сохраненного пользователя
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  updatePassword: async (currentPassword: string, newPassword: string): Promise<{ message: string; user: User }> => {
    const response = await api.put<{ message: string; user: User }>('/auth/profile/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    // Обновляем сохраненного пользователя
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  updateCompanyProfile: async (data: { logo_url?: string; company_name?: string; manager_contact?: string; catalog_description?: string }): Promise<{ message: string; user: User }> => {
    const response = await api.put<{ message: string; user: User }>('/auth/profile/company', data);
    // Обновляем сохраненного пользователя
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },
};

