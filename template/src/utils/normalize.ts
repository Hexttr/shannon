// Утилиты для нормализации данных от backend (snake_case -> camelCase)

export function normalizePentest(pentest: any): any {
  return {
    ...pentest,
    targetUrl: pentest.target_url || pentest.targetUrl,
    createdAt: pentest.created_at || pentest.createdAt,
    startedAt: pentest.started_at || pentest.startedAt,
    completedAt: pentest.completed_at || pentest.completedAt,
    serviceId: pentest.service_id || pentest.serviceId,
  };
}

export function normalizeService(service: any): any {
  return {
    ...service,
    createdAt: service.created_at || service.createdAt,
    updatedAt: service.updated_at || service.updatedAt,
  };
}

export function normalizeVulnerability(vulnerability: any): any {
  return {
    ...vulnerability,
    pentestId: vulnerability.pentest_id || vulnerability.pentestId,
    cvssScore: vulnerability.cvss_score || vulnerability.cvssScore,
    createdAt: vulnerability.created_at || vulnerability.createdAt,
  };
}

export function normalizeLog(log: any): any {
  return {
    ...log,
    pentestId: log.pentest_id || log.pentestId,
  };
}

