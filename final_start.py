"""
Финальный запуск с правильными путями
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def start():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Проверяем структуру venv
        stdin, stdout, stderr = ssh.exec_command(f'cd {SERVER_PATH} && ls -la venv/bin/ | head -5')
        print("Venv bin:")
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        # Находим правильный путь к pip
        stdin, stdout, stderr = ssh.exec_command(f'cd {SERVER_PATH} && which python3')
        python_path = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"\nPython3 path: {python_path}")
        
        # Пересоздаем venv правильно
        print("\nRecreating venv...")
        cmd = f'cd {SERVER_PATH} && rm -rf venv && {python_path} -m venv venv'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        time.sleep(2)
        
        # Устанавливаем зависимости
        print("Installing dependencies...")
        pip_path = f'{SERVER_PATH}/venv/bin/pip3'
        cmd = f'{pip_path} install --upgrade pip'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        # Устанавливаем пакеты по одному для надежности
        packages = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'pydantic-settings',
            'python-jose', 'passlib', 'python-multipart', 'paramiko', 'anthropic',
            'python-socketio', 'aiofiles', 'python-dotenv', 'slowapi', 'markdown'
        ]
        
        for pkg in packages:
            cmd = f'{pip_path} install {pkg}'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
            print(f"  Installed: {pkg}")
        
        # Проверяем импорт
        print("\nTesting import...")
        python_path_full = f'{SERVER_PATH}/venv/bin/python3'
        cmd = f'{python_path_full} -c "import fastapi; print(\\"OK\\")"'
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
        
        cmd = f'cd {SERVER_PATH} && nohup {python_path_full} run.py > server.log 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        print("  OK: Server started")
        print("Waiting 20 seconds...")
        time.sleep(20)
        
        # Проверяем
        stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/health')
        result = stdout.read().decode('utf-8', errors='ignore').strip()
        
        if result:
            print(f"\n{'='*60}")
            print("SUCCESS: Backend is running!")
            print(f"{'='*60}")
            print(f"\nAPI URL: http://{SSH_HOST}:8000")
            print(f"Swagger Docs: http://{SSH_HOST}:8000/docs")
            print(f"ReDoc: http://{SSH_HOST}:8000/redoc")
            print(f"\nHealth: {result}")
            print(f"{'='*60}\n")
        else:
            print("\nLogs:")
            stdin, stdout, stderr = ssh.exec_command(f'tail -50 {SERVER_PATH}/server.log')
            print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    start()

