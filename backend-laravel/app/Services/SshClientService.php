<?php

namespace App\Services;

use phpseclib3\Net\SSH2;

class SshClientService
{
    private ?SSH2 $ssh = null;

    public function __construct()
    {
        $host = config('services.ssh.host', 'localhost');
        $username = config('services.ssh.username', 'root');
        $password = config('services.ssh.password');

        if ($host && $username && $password) {
            $this->ssh = new SSH2($host);
            if (!$this->ssh->login($username, $password)) {
                throw new \RuntimeException('Не удалось подключиться по SSH');
            }
        }
    }

    public function execute(string $command, int $timeout = 600): string
    {
        if (!$this->ssh) {
            // Локальное выполнение команды с таймаутом
            $output = shell_exec("timeout {$timeout} " . $command . ' 2>&1');
            return $output ?? '';
        }

        // Устанавливаем таймаут для SSH соединения (в секундах)
        $this->ssh->setTimeout($timeout);
        
        // Запускаем команду с таймаутом через timeout утилиту
        // Важно: не используем escapeshellarg, так как команда уже содержит переменные окружения и кавычки
        // timeout должен получить команду как есть
        $commandWithTimeout = "timeout {$timeout} {$command} 2>&1";
        
        $result = $this->ssh->exec($commandWithTimeout);
        
        // Если команда не выполнилась из-за timeout, проверяем
        if (empty($result) && $this->ssh->getExitStatus() !== 0) {
            // Пробуем выполнить без timeout для диагностики
            $testResult = $this->ssh->exec($command . ' 2>&1');
            if (!empty($testResult)) {
                return $testResult;
            }
        }
        
        return $result;
    }

    public function __destruct()
    {
        if ($this->ssh) {
            $this->ssh->disconnect();
        }
    }
}

