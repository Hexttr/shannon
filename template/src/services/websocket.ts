import { io, Socket } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

class WebSocketManager {
  private socket: Socket | null = null;

  connect(): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket подключен');
    });

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket отключен');
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribeToPentest(pentestId: number) {
    if (this.socket) {
      this.socket.emit('subscribe_pentest', { pentest_id: pentestId });
    }
  }

  unsubscribeFromPentest(pentestId: number) {
    if (this.socket) {
      this.socket.emit('unsubscribe_pentest', { pentest_id: pentestId });
    }
  }

  onPentestStatus(callback: (data: { pentestId: number; status: string }) => void) {
    if (this.socket) {
      this.socket.on('pentest:status', callback);
    }
  }

  onPentestLog(pentestId: number, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(`pentest:${pentestId}:log`, callback);
    }
  }

  onPentestVulnerability(pentestId: number, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(`pentest:${pentestId}:vulnerability`, callback);
    }
  }

  offPentestStatus(callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off('pentest:status', callback);
    }
  }

  offPentestLog(pentestId: number, callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off(`pentest:${pentestId}:log`, callback);
    }
  }

  offPentestVulnerability(pentestId: number, callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off(`pentest:${pentestId}:vulnerability`, callback);
    }
  }
}

export const wsManager = new WebSocketManager();

