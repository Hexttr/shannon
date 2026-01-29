import { Severity } from '../types';

export function getSeverityColors(severity: Severity) {
  switch (severity) {
    case 'critical':
      return {
        bg: 'bg-red-600',
        text: 'text-red-100',
        border: 'border-red-600',
        light: 'bg-red-500/20',
      };
    case 'high':
      return {
        bg: 'bg-orange-600',
        text: 'text-orange-100',
        border: 'border-orange-600',
        light: 'bg-orange-500/20',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-600',
        text: 'text-yellow-100',
        border: 'border-yellow-600',
        light: 'bg-yellow-500/20',
      };
    case 'low':
      return {
        bg: 'bg-cyan-600',
        text: 'text-cyan-100',
        border: 'border-cyan-600',
        light: 'bg-cyan-500/20',
      };
    default:
      return {
        bg: 'bg-gray-600',
        text: 'text-gray-100',
        border: 'border-gray-600',
        light: 'bg-gray-500/20',
      };
  }
}

export function getSeverityLabel(severity: Severity): string {
  const labels: Record<Severity, string> = {
    critical: 'Критичная',
    high: 'Высокая',
    medium: 'Средняя',
    low: 'Низкая',
    info: 'Информация',
  };
  return labels[severity] || severity;
}


