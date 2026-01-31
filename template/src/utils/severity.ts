export function getSeverityColors(severity: string) {
  switch (severity.toLowerCase()) {
    case 'critical':
      return {
        bg: 'bg-red-600',
        light: 'bg-red-500/20',
        text: 'text-red-400',
        border: 'red',
      };
    case 'high':
      return {
        bg: 'bg-orange-600',
        light: 'bg-orange-500/20',
        text: 'text-orange-400',
        border: 'orange',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-600',
        light: 'bg-yellow-500/20',
        text: 'text-yellow-400',
        border: 'yellow',
      };
    case 'low':
      return {
        bg: 'bg-cyan-600',
        light: 'bg-cyan-500/20',
        text: 'text-cyan-400',
        border: 'cyan',
      };
    default:
      return {
        bg: 'bg-gray-600',
        light: 'bg-gray-500/20',
        text: 'text-gray-400',
        border: 'gray',
      };
  }
}

export function getSeverityLabel(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'Критическая';
    case 'high':
      return 'Высокая';
    case 'medium':
      return 'Средняя';
    case 'low':
      return 'Низкая';
    default:
      return severity;
  }
}

