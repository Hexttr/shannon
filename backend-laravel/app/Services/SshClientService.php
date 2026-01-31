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

    public function execute(string $command): string
    {
        if (!$this->ssh) {
            // Локальное выполнение команды
            $output = shell_exec($command . ' 2>&1');
            return $output ?? '';
        }

        return $this->ssh->exec($command);
    }

    public function __destruct()
    {
        if ($this->ssh) {
            $this->ssh->disconnect();
        }
    }
}

