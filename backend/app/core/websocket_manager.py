"""
Менеджер WebSocket соединений для real-time обновлений
"""
from typing import Dict, Set
import socketio
import logging

logger = logging.getLogger(__name__)

# Создаем Socket.IO сервер
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

# Хранилище активных соединений по pentest_id
_connections: Dict[int, Set[str]] = {}


@sio.event
async def connect(sid, environ):
    """Обработка подключения клиента"""
    logger.info(f"Клиент подключен: {sid}")
    return True


@sio.event
async def disconnect(sid):
    """Обработка отключения клиента"""
    logger.info(f"Клиент отключен: {sid}")
    # Удаляем из всех комнат
    for pentest_id in list(_connections.keys()):
        _connections[pentest_id].discard(sid)
        if not _connections[pentest_id]:
            del _connections[pentest_id]


@sio.event
async def subscribe_pentest(sid, data):
    """Подписка на обновления конкретного пентеста"""
    pentest_id = data.get('pentest_id')
    if pentest_id:
        if pentest_id not in _connections:
            _connections[pentest_id] = set()
        _connections[pentest_id].add(sid)
        await sio.enter_room(sid, f"pentest_{pentest_id}")
        logger.info(f"Клиент {sid} подписан на пентест {pentest_id}")


@sio.event
async def unsubscribe_pentest(sid, data):
    """Отписка от обновлений пентеста"""
    pentest_id = data.get('pentest_id')
    if pentest_id and pentest_id in _connections:
        _connections[pentest_id].discard(sid)
        await sio.leave_room(sid, f"pentest_{pentest_id}")
        logger.info(f"Клиент {sid} отписан от пентеста {pentest_id}")


async def emit_pentest_status(pentest_id: int, status: str):
    """Отправка обновления статуса пентеста"""
    await sio.emit('pentest:status', {
        'pentestId': pentest_id,
        'status': status
    }, room=f"pentest_{pentest_id}")
    await sio.emit('pentest:status', {
        'pentestId': pentest_id,
        'status': status
    }, room='all')  # Для всех подписанных на общий канал


async def emit_pentest_log(pentest_id: int, log_data: dict):
    """Отправка нового лога пентеста"""
    await sio.emit(f'pentest:{pentest_id}:log', log_data, room=f"pentest_{pentest_id}")


async def emit_pentest_vulnerability(pentest_id: int, vulnerability_data: dict):
    """Отправка новой уязвимости"""
    await sio.emit(f'pentest:{pentest_id}:vulnerability', vulnerability_data, room=f"pentest_{pentest_id}")


