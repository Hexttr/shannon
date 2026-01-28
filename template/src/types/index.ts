// Типы для приложения

export type PentestStatus = 'pending' | 'running' | 'completed' | 'failed' | 'stopped';

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type LogLevel = 'info' | 'warning' | 'error' | 'debug';

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Service {
  id: number;
  name: string;
  url: string;
  created_at: string;
  updated_at?: string;
  createdAt?: string; // Для совместимости
  updatedAt?: string; // Для совместимости
}

export interface CreateServiceRequest {
  name: string;
  url: string;
}

export interface UpdateServiceRequest {
  name?: string;
  url?: string;
}

export interface Pentest {
  id: number;
  name: string;
  service_id?: number;
  target_url: string;
  status: PentestStatus;
  config?: Record<string, any>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  createdAt?: string; // Для совместимости
  startedAt?: string; // Для совместимости
  completedAt?: string; // Для совместимости
}

export interface CreatePentestRequest {
  name: string;
  target_url: string;
  config?: Record<string, any>;
}

export interface Vulnerability {
  id: number;
  pentest_id: number;
  type: string;
  title: string;
  severity: Severity;
  description?: string;
  location?: string;
  cvss_score?: number;
  exploit?: string;
  recommendation?: string;
  created_at: string;
}

export interface Log {
  id: number;
  pentest_id: number;
  level: LogLevel;
  message: string;
  timestamp: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

