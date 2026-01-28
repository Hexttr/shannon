"""
Финальное развертывание с правильной установкой
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Connected")
        
        # Удаляем старый venv и создаем новый
        print("Creating virtual environment...")
        cmd = f'cd {SERVER_PATH} && rm -rf venv && python3 -m venv venv'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        print("  OK: venv created")
        
        # Устанавливаем зависимости
        print("Installing dependencies...")
        cmd = f'cd {SERVER_PATH} && venv/bin/pip install --quiet --upgrade pip && venv/bin/pip install --quiet -r requirements.txt'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        if 'error' in error.lower() and 'already satisfied' not in error.lower():
            print(f"  WARNING: {error[:300]}")
        print("  OK: Dependencies installed")
        
        # Тестируем импорт
        print("Testing import...")
        cmd = f'cd {SERVER_PATH} && venv/bin/python -c "from app.main import socketio_app; print(\\"Import OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        if 'Import OK' in output:
            print("  OK: Import successful")
        else:
            print(f"  ERROR: {error}")
            return
        
        # Останавливаем старые процессы
        print("Stopping old processes...")
        ssh.exec_command('pkill -f "python.*run.py" || pkill -f "uvicorn" || true')
        time.sleep(2)
        
        # Запускаем сервер
        print("Starting server...")
        cmd = f'cd {SERVER_PATH} && nohup venv/bin/python run.py > server.log 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        print("  OK: Server started")
        
        # Ждем
        print("Waiting for server to start...")
        time.sleep(10)
        
        # Проверяем health
        for i in range(3):
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
            time.sleep(3)
        
        # Показываем логи если не запустился
        print("\nServer not responding. Checking logs...")
        stdin, stdout, stderr = ssh.exec_command(f'tail -50 {SERVER_PATH}/server.log')
        log = stdout.read().decode('utf-8', errors='ignore')
        print(log)
        
        # Проверяем процессы
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep python | grep -v grep')
        print("\nPython processes:")
        print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()

