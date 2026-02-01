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
            // Оборачиваем команду в bash -c с одинарными кавычками для правильной обработки
            $escapedCommand = str_replace("'", "'\\''", $command);
            $output = shell_exec("timeout {$timeout} bash -c '{$escapedCommand}' 2>&1");
            return $output ?? '';
        }

        // Устанавливаем таймаут для SSH соединения (в секундах)
        $this->ssh->setTimeout($timeout);
        
        // Запускаем команду с таймаутом через timeout утилиту
        // Важно: оборачиваем команду в bash -c с одинарными кавычками
        // Это позволяет правильно обработать команды с пробелами, кавычками и переменными окружения
        // Экранируем одинарные кавычки в команде: ' -> '\''
        $escapedCommand = str_replace("'", "'\\''", $command);
        $commandWithTimeout = "timeout {$timeout} bash -c '{$escapedCommand}' 2>&1";
        
        return $this->ssh->exec($commandWithTimeout);
    }

    public function __destruct()
    {
        if ($this->ssh) {
            $this->ssh->disconnect();
        }
    }
}

