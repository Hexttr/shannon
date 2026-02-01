import api from './api';
import type { Service, CreateServiceRequest, UpdateServiceRequest } from '../types';

export const serviceApi = {
  getAll: async () => {
    const response = await api.get<{ data: Service[] }>('/services');
    // Laravel возвращает { data: [...] }, поэтому возвращаем response.data.data
    return { ...response, data: response.data.data };
  },

  create: async (data: CreateServiceRequest) => {
    const response = await api.post<{ data: Service }>('/services', data);
    return { ...response, data: response.data.data };
  },

  update: async (id: string, data: UpdateServiceRequest) => {
    const response = await api.put<{ data: Service }>(`/services/${id}`, data);
    return { ...response, data: response.data.data };
  },

  delete: async (id: string) => {
    const response = await api.delete(`/services/${id}`);
    return response;
  },
};

