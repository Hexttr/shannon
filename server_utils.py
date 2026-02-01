#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для работы с сервером через SSH (paramiko)
"""

import paramiko
import os
import sys

# Настройка кодировки для Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Данные сервера
SERVER_HOST = "72.56.79.153"
SERVER_USER = "root"
SERVER_PASSWORD = "m8J@2_6whwza6U"
SERVER_PORT = 22

class ServerConnection:
    """Класс для работы с сервером через SSH"""
    
    def __init__(self):
        self.ssh = None
        self.connected = False
    
    def connect(self):
        """Подключается к серверу"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=SERVER_HOST,
                port=SERVER_PORT,
                username=SERVER_USER,
                password=SERVER_PASSWORD,
                timeout=10
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка подключения: {e}")
            return False
    
    def execute(self, command):
        """Выполняет команду на сервере и возвращает результат"""
        if not self.connected:
            if not self.connect():
                return None, None
        
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            return output, error, exit_code
        except Exception as e:
            print(f"[ERROR] Ошибка выполнения команды: {e}")
            return None, str(e), -1
    
    def close(self):
        """Закрывает соединение"""
        if self.ssh:
            self.ssh.close()
            self.connected = False
    
    def __enter__(self):
        """Контекстный менеджер: вход"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход"""
        self.close()

def get_server_connection():
    """Возвращает подключение к серверу"""
    conn = ServerConnection()
    if conn.connect():
        return conn
    return None

