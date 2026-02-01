import axios from 'axios';

// Автоматически определяем API URL на основе текущего протокола
const getApiUrl = () => {
  // Если указана переменная окружения - используем её
  if (import.meta.env.VITE_API_URL) {
    console.log('[API] Используется VITE_API_URL:', import.meta.env.VITE_API_URL);
    return import.meta.env.VITE_API_URL;
  }
  
  // В production используем тот же протокол и хост, что и текущая страница
  // ВАЖНО: Если страница загружена по HTTPS, API тоже должен быть HTTPS
  const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
  
  if (isProduction) {
    // Используем тот же протокол что и текущая страница (HTTPS если страница HTTPS)
    // ВАЖНО: window.location.protocol уже содержит ':' в конце ('https:' или 'http:')
    const protocol = window.location.protocol; // 'https:' или 'http:'
    const host = window.location.host; // '72.56.79.153' или '72.56.79.153:443'
    
    // Убираем порт если он стандартный (80 для HTTP, 443 для HTTPS)
    const hostWithoutPort = host.split(':')[0];
    
    // Формируем URL БЕЗ порта 8000
    const apiUrl = `${protocol}//${hostWithoutPort}/api`;
    console.log('[API] Production URL определен:', apiUrl, {
      protocol,
      host,
      hostWithoutPort,
      fullLocation: window.location.href
    });
    return apiUrl;
  }
  
  // В development используем localhost
  const devUrl = 'http://localhost:8000/api';
  console.log('[API] Используется dev URL:', devUrl);
  return devUrl;
};

// ВАЖНО: Для production жестко задаем правильный URL
let API_URL = getApiUrl();

// Дополнительная проверка: если в production и URL содержит :8000, исправляем
if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
  if (API_URL.includes(':8000')) {
    console.warn('[API] Обнаружен неправильный URL с :8000, исправляем...');
    const protocol = window.location.protocol;
    const host = window.location.host.split(':')[0];
    API_URL = `${protocol}//${host}/api`;
    console.log('[API] Исправленный API_URL:', API_URL);
  }
}

console.log('[API] Финальный API_URL:', API_URL);

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
    // Логируем ошибки для отладки
    console.error('[API Error]', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL,
      },
    });

    // Обработка сетевых ошибок (нет ответа от сервера)
    if (!error.response) {
      console.error('[API Error] Network error:', error.message);
      // Создаем более информативную ошибку
      const networkError = new Error(
        error.message === 'Network Error' 
          ? 'Не удалось подключиться к серверу. Проверьте подключение к интернету.'
          : error.message
      );
      (networkError as any).isNetworkError = true;
      return Promise.reject(networkError);
    }

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

