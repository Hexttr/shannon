from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.config import settings
from app.database import init_db
from app.api import auth, services, pentests, vulnerabilities, logs, reports
from app.core.websocket_manager import sio
import logging

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Shannon Pentest Platform API",
    description="API для платформы автоматизированного пентестинга",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO приложение (обертка над FastAPI app)
socketio_app = socketio.ASGIApp(sio, app)

# Для запуска используйте: uvicorn app.main:socketio_app --reload

# Подключение роутеров
app.include_router(auth.router)
app.include_router(services.router)
app.include_router(pentests.router)
app.include_router(vulnerabilities.router)
app.include_router(logs.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    init_db()
    logging.info("🚀 Shannon Pentest Platform запущен")
    logging.info("📡 WebSocket сервер готов")


# Примечание: для запуска с WebSocket используйте socketio_app вместо app
# uvicorn app.main:socketio_app --reload
# Но для совместимости оставляем app как основное приложение
# WebSocket будет работать через отдельный endpoint если нужно


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "message": "Shannon Pentest Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Проверка здоровья API"""
    return {"status": "ok"}

