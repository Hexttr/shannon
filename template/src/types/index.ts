export interface User {
  id: string;
  username: string;
  email: string;
  created_at?: string;
  updated_at?: string;
}

export interface Service {
  id: string;
  name: string;
  url: string;
  created_at: string;
  updated_at: string;
}

export interface Pentest {
  id: string;
  name: string;
  target_url: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
  current_step?: string;
  step_progress?: Record<string, string>;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Vulnerability {
  id: string;
  pentest_id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  cvss_score?: string;
  cve?: string;
  solution?: string;
  created_at: string;
}

export interface Log {
  id: string;
  pentest_id: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

export interface CreateServiceRequest {
  name: string;
  url: string;
}

export interface CreatePentestRequest {
  name: string;
  config: {
    targetUrl: string;
  };
}

