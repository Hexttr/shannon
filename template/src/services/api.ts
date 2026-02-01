import axios from 'axios';

// Автоматически определяем API URL на основе текущего протокола
const getApiUrl = () => {
  // Если указана переменная окружения - используем её
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // В production используем тот же протокол и хост, что и текущая страница
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return `${window.location.protocol}//${window.location.host}/api`;
  }
  
  // В development используем localhost
  return 'http://localhost:8000/api';
};

const API_URL = getApiUrl();

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Добавляем токен к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Обрабатываем ошибки авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Выкидываем пользователя только при реальной 401 ошибке (не при таймаутах)
    if (error.response?.status === 401 && error.response?.statusText !== 'Gateway Timeout') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      // Не редиректим сразу, даем возможность обработать ошибку
      if (window.location.pathname !== '/') {
        setTimeout(() => {
          window.location.href = '/';
        }, 100);
      }
    }
    // При таймаутах (504, 502) не выкидываем пользователя
    return Promise.reject(error);
  }
);

export default api;

