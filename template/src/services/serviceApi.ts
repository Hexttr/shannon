import api from './api';
import { Service, CreateServiceRequest, UpdateServiceRequest } from '../types';
import { normalizeService } from '../utils/normalize';

export const serviceApi = {
  getAll: async (): Promise<{ data: Service[] }> => {
    const response = await api.get<Service[]>('/api/services');
    return { data: response.data.map(normalizeService) };
  },

  getById: async (id: number): Promise<{ data: Service }> => {
    const response = await api.get<Service>(`/api/services/${id}`);
    return { data: normalizeService(response.data) };
  },

  create: async (data: CreateServiceRequest): Promise<{ data: Service }> => {
    return api.post<Service>('/api/services', data);
  },

  update: async (id: number, data: UpdateServiceRequest): Promise<{ data: Service }> => {
    return api.put<Service>(`/api/services/${id}`, data);
  },

  delete: async (id: number): Promise<void> => {
    return api.delete(`/api/services/${id}`);
  },
};


