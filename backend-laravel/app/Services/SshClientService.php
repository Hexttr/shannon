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
            $output = shell_exec("timeout {$timeout} " . escapeshellarg($command) . ' 2>&1');
            return $output ?? '';
        }

        // Устанавливаем таймаут для SSH соединения
        $this->ssh->setTimeout($timeout);
        
        // Запускаем команду с таймаутом через timeout утилиту
        // Используем правильное экранирование для команды
        $commandWithTimeout = "timeout {$timeout} bash -c " . escapeshellarg($command) . " 2>&1";
        
        return $this->ssh->exec($commandWithTimeout);
    }

    public function __destruct()
    {
        if ($this->ssh) {
            $this->ssh->disconnect();
        }
    }
}

