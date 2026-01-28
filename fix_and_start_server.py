"""
Исправление структуры и запуск сервера
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'

def fix_and_start():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Connected to server")
        
        # Проверяем структуру
        stdin, stdout, stderr = ssh.exec_command('cd /root/shannon/backend && ls -la app/')
        print("App directory:")
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        # Устанавливаем зависимости если нужно
        print("\nInstalling dependencies...")
        cmd = """cd /root/shannon/backend && \
source venv/bin/activate && \
pip install -q fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib python-multipart paramiko anthropic python-socketio aiofiles python-dotenv slowapi markdown weasyprint markdown2 xhtml2pdf"""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        print("Dependencies installed")
        
        # Останавливаем старый процесс если есть
        print("\nStopping old processes...")
        ssh.exec_command('pkill -f "python.*run.py" || true')
        time.sleep(2)
        
        # Запускаем сервер
        print("\nStarting server...")
        cmd = """cd /root/shannon/backend && \
source venv/bin/activate && \
nohup python run.py > server.log 2>&1 &"""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        # Ждем запуска
        print("Waiting for server to start...")
        time.sleep(5)
        
        # Проверяем health
        for i in range(5):
            stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/health')
            result = stdout.read().decode('utf-8', errors='ignore').strip()
            if result:
                print(f"\n{'='*60}")
                print("SUCCESS: Backend is running!")
                print(f"{'='*60}")
                print(f"\nAPI URL: http://{SSH_HOST}:8000")
                print(f"Swagger Docs: http://{SSH_HOST}:8000/docs")
                print(f"ReDoc: http://{SSH_HOST}:8000/redoc")
                print(f"\nHealth check: {result}")
                print(f"{'='*60}\n")
                return
            time.sleep(2)
        
        # Если не ответил, показываем логи
        print("\nServer not responding, checking logs...")
        stdin, stdout, stderr = ssh.exec_command('tail -30 /root/shannon/backend/server.log')
        print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_and_start()

