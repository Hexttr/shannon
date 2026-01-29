import paramiko
from typing import Optional, List, Tuple
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SSHClient:
    """Клиент для SSH подключения к серверу"""
    
    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.host = settings.ssh_host
        self.user = settings.ssh_user
        self.password = settings.ssh_password
        self.port = settings.ssh_port
    
    def connect(self) -> bool:
        """Подключение к серверу"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.host,
                username=self.user,
                password=self.password,
                port=self.port,
                timeout=10
            )
            logger.info(f"✅ Подключение к серверу {self.host} установлено")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к серверу: {e}")
            return False
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("Отключение от сервера")
    
    def execute_command(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """
        Выполнение команды на сервере
        Returns: (exit_code, stdout, stderr)
        """
        if not self.client:
            if not self.connect():
                raise ConnectionError("Не удалось подключиться к серверу")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8', errors='ignore')
            stderr_text = stderr.read().decode('utf-8', errors='ignore')
            
            return exit_code, stdout_text, stderr_text
        except Exception as e:
            logger.error(f"Ошибка выполнения команды '{command}': {e}")
            raise
    
    def check_tool_installed(self, tool_name: str) -> bool:
        """Проверка установлен ли инструмент"""
        try:
            exit_code, _, _ = self.execute_command(f"which {tool_name}")
            return exit_code == 0
        except:
            return False
    
    def install_tool(self, tool_name: str, install_command: str) -> bool:
        """Установка инструмента на сервере"""
        try:
            logger.info(f"Установка {tool_name}...")
            exit_code, stdout, stderr = self.execute_command(install_command, timeout=600)
            if exit_code == 0:
                logger.info(f"✅ {tool_name} успешно установлен")
                return True
            else:
                logger.error(f"❌ Ошибка установки {tool_name}: {stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Исключение при установке {tool_name}: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


