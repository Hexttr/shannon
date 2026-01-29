#!/usr/bin/env python3
"""
Добавление проверки на self-scanning и системы отслеживания workflow
"""

# 1. Проверка на self-scanning
self_scan_check = '''
    def _check_self_scanning(self):
        """Проверка, не сканируем ли мы сами себя"""
        from app.config import settings
        
        # Получаем IP сервера из настроек SSH
        server_host = settings.ssh_host
        
        # Извлекаем хост из target_url
        target_host = self.target_url.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Убираем порт если есть
        target_host = target_host.split(":")[0]
        
        # Проверяем совпадение
        if target_host == server_host or target_host in ["localhost", "127.0.0.1", "0.0.0.0"]:
            raise ValueError(
                f"⚠️ ОШИБКА: Попытка сканировать сам сервер ({server_host}). "
                f"Это white box сканирование и может привести к проблемам. "
                f"Используйте внешний ресурс для black box сканирования."
            )
        
        # Дополнительная проверка через DNS резолвинг
        try:
            import socket
            target_ip = socket.gethostbyname(target_host)
            server_ip = socket.gethostbyname(server_host)
            
            if target_ip == server_ip:
                raise ValueError(
                    f"⚠️ ОШИБКА: IP адрес цели ({target_ip}) совпадает с IP сервера. "
                    f"Это white box сканирование."
                )
        except Exception as e:
            logger.warning(f"Не удалось проверить IP через DNS: {e}")
        
        self.add_log(LogLevel.INFO, f"✅ Проверка пройдена: сканирование внешнего ресурса ({target_host})")
'''

# 2. Система отслеживания workflow
workflow_tracking = '''
# Добавить в модель Pentest (backend/app/models/pentest.py):
current_step = Column(String, nullable=True)  # Текущий шаг: "nmap", "nikto", "nuclei", "dirb", "sqlmap", "completed"
step_progress = Column(JSON, nullable=True)  # Прогресс по шагам: {"nmap": "completed", "nikto": "running", ...}

# В PentestEngine добавить методы:
def _set_step(self, step_name: str, status: str = "running"):
    """Установка текущего шага workflow"""
    self.pentest.current_step = step_name
    if not self.pentest.step_progress:
        self.pentest.step_progress = {}
    self.pentest.step_progress[step_name] = status
    self.db.commit()
    
    # Отправляем через WebSocket
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(emit_pentest_status(self.pentest_id, PentestStatus.RUNNING.value))
        else:
            loop.run_until_complete(emit_pentest_status(self.pentest_id, PentestStatus.RUNNING.value))
    except Exception as e:
        logger.warning(f"Не удалось отправить статус шага через WebSocket: {e}")

def _get_workflow_status(self) -> Dict[str, str]:
    """Получение статуса workflow"""
    return self.pentest.step_progress or {}
'''

print("="*60)
print("РЕШЕНИЯ ДЛЯ ВОПРОСОВ")
print("="*60)
print("\n1. ПРОВЕРКА НА SELF-SCANNING:")
print(self_scan_check)
print("\n2. СИСТЕМА ОТСЛЕЖИВАНИЯ WORKFLOW:")
print(workflow_tracking)

