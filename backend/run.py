"""
Скрипт для запуска приложения с поддержкой WebSocket
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.main import socketio_app

if __name__ == "__main__":
    uvicorn.run(
        socketio_app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Отключаем reload для стабильности
        log_level="info"
    )

