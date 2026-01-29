import { useEffect, useRef } from 'react';
import { Log } from '../types';

interface LogViewerProps {
  logs: Log[];
  autoScroll?: boolean;
  maxHeight?: string;
  isLoading?: boolean;
}

export default function LogViewer({
  logs,
  autoScroll = true,
  maxHeight = '400px',
  isLoading = false,
}: LogViewerProps) {
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
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
      case 'info':
        return 'text-blue-400';
      case 'debug':
        return 'text-gray-400';
      default:
        return 'text-gray-300';
    }
  };

  if (isLoading && logs.length === 0) {
    return (
      <div className="text-center py-4 text-gray-500">
        Загрузка логов...
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="text-center py-4 text-gray-500">
        Логи отсутствуют
      </div>
    );
  }

  return (
    <div
      ref={logContainerRef}
      className="font-mono text-xs overflow-y-auto bg-black/50 rounded p-3"
      style={{ maxHeight }}
    >
      {logs.map((log) => (
        <div key={log.id} className="mb-1">
          <span className="text-gray-500">
            {new Date(log.timestamp).toLocaleTimeString('ru-RU')}
          </span>
          <span className={`ml-2 ${getLogColor(log.level)}`}>
            [{log.level.toUpperCase()}]
          </span>
          <span className="ml-2 text-gray-300">{log.message}</span>
        </div>
      ))}
    </div>
  );
}


