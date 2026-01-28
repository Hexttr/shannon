import api from './api';
import { Service, CreateServiceRequest, UpdateServiceRequest } from '../types';

export const serviceApi = {
  getAll: async (): Promise<{ data: Service[] }> => {
    return api.get<Service[]>('/api/services');
  },

  getById: async (id: number): Promise<{ data: Service }> => {
    return api.get<Service>(`/api/services/${id}`);
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

