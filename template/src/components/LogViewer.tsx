import React from 'react';

interface Log {
  id: string;
  message: string;
  level: 'info' | 'warning' | 'error';
  timestamp: string;
}

interface LogViewerProps {
  logs: Log[];
  autoScroll?: boolean;
  maxHeight?: string;
  isLoading?: boolean;
}

export default function LogViewer({ logs, autoScroll = true, maxHeight = '400px', isLoading = false }: LogViewerProps) {
  const logContainerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-gray-300';
    }
  };

  return (
    <div
      ref={logContainerRef}
      className="font-mono text-xs overflow-y-auto bg-gray-900 rounded p-3"
      style={{ maxHeight }}
    >
      {isLoading && logs.length === 0 && (
        <div className="text-gray-500">Загрузка логов...</div>
      )}
      {logs.length === 0 && !isLoading && (
        <div className="text-gray-500">Логи отсутствуют</div>
      )}
      {logs.map((log) => (
        <div key={log.id} className="mb-1">
          <span className="text-gray-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
          <span className={getLogColor(log.level)}>{log.message}</span>
        </div>
      ))}
    </div>
  );
}

