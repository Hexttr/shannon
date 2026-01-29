import { useQuery } from '@tanstack/react-query';
import { pentestApi } from '../services/pentestApi';
import { Pentest } from '../types';
import {
  FiLoader,
  FiCheckCircle,
  FiXCircle,
  FiClock,
  FiPlay,
  FiShield,
} from 'react-icons/fi';

const WORKFLOW_STEPS = [
  { id: 'nmap', name: 'Nmap Scan', description: 'Сканирование портов и сервисов', icon: '🔍' },
  { id: 'nikto', name: 'Nikto Scan', description: 'Сканирование веб-сервера', icon: '🌐' },
  { id: 'nuclei', name: 'Nuclei Scan', description: 'Сканирование уязвимостей', icon: '🎯' },
  { id: 'dirb', name: 'Dirb Scan', description: 'Поиск директорий', icon: '📁' },
  { id: 'sqlmap', name: 'SQLMap Scan', description: 'Проверка SQL инъекций', icon: '💉' },
];

function getStepStatus(stepId: string, stepProgress?: Record<string, string>, currentStep?: string): 'pending' | 'running' | 'completed' | 'failed' {
  if (!stepProgress) {
    if (currentStep === stepId) return 'running';
    return 'pending';
  }
  
  const status = stepProgress[stepId];
  if (status === 'completed') return 'completed';
  if (status === 'failed') return 'failed';
  if (status === 'running' || currentStep === stepId) return 'running';
  return 'pending';
}

function StepIcon({ status }: { status: 'pending' | 'running' | 'completed' | 'failed' }) {
  switch (status) {
    case 'completed':
      return <FiCheckCircle className="w-6 h-6 text-green-400" />;
    case 'failed':
      return <FiXCircle className="w-6 h-6 text-red-400" />;
    case 'running':
      return <FiLoader className="w-6 h-6 text-blue-400 animate-spin" />;
    default:
      return <FiClock className="w-6 h-6 text-gray-500" />;
  }
}

function StepCard({ 
  step, 
  status, 
  isActive 
}: { 
  step: typeof WORKFLOW_STEPS[0]; 
  status: 'pending' | 'running' | 'completed' | 'failed';
  isActive: boolean;
}) {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-500/10';
      case 'failed':
        return 'border-red-500 bg-red-500/10';
      case 'running':
        return 'border-blue-500 bg-blue-500/10 animate-pulse';
      default:
        return 'border-gray-700 bg-gray-800/50';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return 'Завершено';
      case 'failed':
        return 'Ошибка';
      case 'running':
        return 'Выполняется...';
      default:
        return 'Ожидание';
    }
  };

  return (
    <div
      className={`rounded-lg border-2 p-4 transition-all duration-300 ${
        isActive ? getStatusColor() : 'border-gray-700 bg-gray-800/50'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <StepIcon status={status} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">{step.icon}</span>
            <h3 className="text-lg font-semibold text-white">{step.name}</h3>
          </div>
          <p className="text-sm text-gray-400 mb-2">{step.description}</p>
          <div className="flex items-center gap-2">
            <span
              className={`text-xs font-medium px-2 py-1 rounded ${
                status === 'completed'
                  ? 'bg-green-500/20 text-green-400'
                  : status === 'failed'
                  ? 'bg-red-500/20 text-red-400'
                  : status === 'running'
                  ? 'bg-blue-500/20 text-blue-400'
                  : 'bg-gray-700/50 text-gray-500'
              }`}
            >
              {getStatusText()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Workflow() {
  const { data: pentests = [], isLoading } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then((res) => res.data),
    refetchInterval: 3000, // Обновление каждые 3 секунды
  });

  // Находим активный пентест (running или последний запущенный)
  const activePentest = 
    pentests.find((p) => p.status === 'running') || 
    pentests.find((p) => p.status === 'completed' && p.startedAt) ||
    pentests[0];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <FiLoader className="w-8 h-8 text-gray-400 animate-spin" />
      </div>
    );
  }

  if (!activePentest) {
    return (
      <div className="min-h-screen bg-black">
        <div className="p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
              <FiShield className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Нет активных пентестов</h2>
              <p className="text-gray-400">Создайте новый пентест для отслеживания workflow</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const stepProgress = (activePentest as any).step_progress || {};
  const currentStep = (activePentest as any).current_step || '';

  // Вычисляем общий прогресс
  const completedSteps = WORKFLOW_STEPS.filter(
    (step) => getStepStatus(step.id, stepProgress, currentStep) === 'completed'
  ).length;
  const totalSteps = WORKFLOW_STEPS.length;
  const progressPercent = (completedSteps / totalSteps) * 100;

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">
                Workflow Пентеста
              </h1>
              <p className="text-sm text-gray-400">
                Отслеживание прогресса выполнения пентеста
              </p>
            </div>
            {activePentest && (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm text-gray-400">Пентест</p>
                  <p className="text-lg font-semibold text-white truncate max-w-xs">
                    {activePentest.name}
                  </p>
                </div>
                <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/30">
                  <FiShield className="w-6 h-6 text-red-400" />
                </div>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-300">Общий прогресс</span>
              <span className="text-sm font-bold text-white">
                {completedSteps}/{totalSteps} шагов
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-red-600 to-red-800 h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {progressPercent.toFixed(0)}% завершено
            </p>
          </div>

          {/* Workflow Steps */}
          <div className="space-y-4">
            {WORKFLOW_STEPS.map((step, index) => {
              const status = getStepStatus(step.id, stepProgress, currentStep);
              const isActive = currentStep === step.id || status === 'running';

              return (
                <div key={step.id} className="relative">
                  {/* Connection Line */}
                  {index < WORKFLOW_STEPS.length - 1 && (
                    <div
                      className={`absolute left-7 top-16 w-0.5 h-4 ${
                        status === 'completed'
                          ? 'bg-green-500'
                          : status === 'failed'
                          ? 'bg-red-500'
                          : 'bg-gray-700'
                      }`}
                    />
                  )}
                  <StepCard step={step} status={status} isActive={isActive} />
                </div>
              );
            })}
          </div>

          {/* Current Step Info */}
          {currentStep && (
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 rounded-xl p-4 border border-blue-700/50">
              <div className="flex items-center gap-2">
                <FiPlay className="w-5 h-5 text-blue-400" />
                <span className="text-sm font-medium text-blue-300">
                  Текущий шаг: {WORKFLOW_STEPS.find((s) => s.id === currentStep)?.name || currentStep}
                </span>
              </div>
            </div>
          )}

          {/* Pentest Info */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Информация о пентесте</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400 mb-1">Цель</p>
                <p className="text-sm font-mono text-cyan-400 break-all">
                  {activePentest.target_url || (activePentest as any).target_url}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Статус</p>
                <p className="text-sm font-semibold text-white capitalize">
                  {activePentest.status}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Запущен</p>
                <p className="text-sm text-gray-300">
                  {activePentest.startedAt
                    ? new Date(activePentest.startedAt).toLocaleString('ru-RU')
                    : 'Не запущен'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Завершен</p>
                <p className="text-sm text-gray-300">
                  {activePentest.completedAt
                    ? new Date(activePentest.completedAt).toLocaleString('ru-RU')
                    : 'В процессе'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

