#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

stdin, stdout, stderr = ssh.exec_command("tail -30 /root/shannon/backend-laravel/storage/logs/laravel.log | grep ERROR | tail -5")
print(stdout.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
print(stdout.read().decode('utf-8'))

ssh.close()


