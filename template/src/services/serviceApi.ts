import api from './api';
import type { Service, CreateServiceRequest } from '../types';

export const serviceApi = {
  getAll: async () => {
    const response = await api.get<{ data: Service[] }>('/services');
    return response;
  },

  create: async (data: CreateServiceRequest) => {
    const response = await api.post<{ data: Service }>('/services', data);
    return response;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/services/${id}`);
    return response;
  },
};

