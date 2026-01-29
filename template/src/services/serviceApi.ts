import api from './api';
import { Service, CreateServiceRequest, UpdateServiceRequest } from '../types';
import { normalizeService } from '../utils/normalize';

export const serviceApi = {
  getAll: async (): Promise<{ data: Service[] }> => {
    const response = await api.get<Service[]>('/services');
    return { data: response.data.map(normalizeService) };
  },

  getById: async (id: number): Promise<{ data: Service }> => {
    const response = await api.get<Service>(`/services/${id}`);
    return { data: normalizeService(response.data) };
  },

  create: async (data: CreateServiceRequest): Promise<{ data: Service }> => {
    return api.post<Service>('/services', data);
  },

  update: async (id: number, data: UpdateServiceRequest): Promise<{ data: Service }> => {
    return api.put<Service>(`/services/${id}`, data);
  },

  delete: async (id: number): Promise<void> => {
    return api.delete(`/services/${id}`);
  },
};


