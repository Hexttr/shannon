"""
Правильная установка и запуск
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def install():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Используем bash -c для правильной активации
        print("Installing dependencies...")
        cmd = f"""bash -c 'cd {SERVER_PATH} && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt'"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # Ждем завершения
        import select
        import sys
        
        while True:
            if stdout.channel.exit_status_ready():
                break
            time.sleep(1)
        
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("  OK: Dependencies installed")
        else:
            print(f"  WARNING: Exit code {exit_status}")
            if error:
                print(f"  Error: {error[:500]}")
        
        # Проверяем что установлено
        print("\nChecking installed packages...")
        cmd = f'cd {SERVER_PATH} && venv/bin/pip list | grep -i fastapi'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8', errors='ignore')
        if result:
            print(f"  OK: {result.strip()}")
        else:
            print("  WARNING: FastAPI not found")
        
        # Тестируем импорт
        print("\nTesting import...")
        cmd = f'cd {SERVER_PATH} && venv/bin/python -c "import fastapi; print(\\"OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        if 'OK' in output:
            print("  OK: Import successful")
        else:
            error = stderr.read().decode('utf-8', errors='ignore')
            print(f"  ERROR: {error}")
            return
        
        # Запускаем сервер
        print("\nStarting server...")
        ssh.exec_command('pkill -f "python.*run.py" || true')
        time.sleep(2)
        
        cmd = f"""bash -c 'cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup python run.py > server.log 2>&1 &'"""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        print("  OK: Server started")
        print("Waiting 20 seconds for server to start...")
        time.sleep(20)
        
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
            time.sleep(5)
        
        # Показываем логи
        print("\nServer not responding. Logs:")
        stdin, stdout, stderr = ssh.exec_command(f'tail -100 {SERVER_PATH}/server.log')
        print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    install()

