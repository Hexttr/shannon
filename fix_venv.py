"""
Исправление venv и установка
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def fix():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Удаляем venv и создаем правильно с ensurepip
        print("Creating venv with ensurepip...")
        cmd = f'cd {SERVER_PATH} && rm -rf venv && python3 -m venv venv --system-site-packages'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        time.sleep(2)
        
        # Устанавливаем pip в venv
        print("Installing pip in venv...")
        cmd = f'cd {SERVER_PATH} && venv/bin/python3 -m ensurepip --upgrade'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        time.sleep(2)
        
        # Проверяем что pip есть
        stdin, stdout, stderr = ssh.exec_command(f'cd {SERVER_PATH} && test -f venv/bin/pip && echo "EXISTS" || echo "NOT_EXISTS"')
        result = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"Pip exists: {result}")
        
        if 'NOT_EXISTS' in result:
            # Устанавливаем pip вручную
            print("Installing pip manually...")
            cmd = f'cd {SERVER_PATH} && venv/bin/python3 -m pip install --upgrade pip'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
        
        # Устанавливаем зависимости через python -m pip
        print("\nInstalling dependencies via python -m pip...")
        python_cmd = f'{SERVER_PATH}/venv/bin/python3'
        pip_cmd = f'{python_cmd} -m pip'
        
        packages = 'fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib python-multipart paramiko anthropic python-socketio aiofiles python-dotenv slowapi markdown weasyprint markdown2 xhtml2pdf'.split()
        
        for pkg in packages:
            cmd = f'{pip_cmd} install {pkg}'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
            print(f"  Installed: {pkg}")
        
        # Проверяем импорт
        print("\nTesting import...")
        cmd = f'{python_cmd} -c "import fastapi; import uvicorn; print(\\"OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        if 'OK' in output:
            print("  OK: Import successful")
        else:
            print(f"  ERROR: {error}")
            return
        
        # Запускаем сервер
        print("\nStarting server...")
        ssh.exec_command('pkill -f "python.*run.py" || true')
        time.sleep(2)
        
        cmd = f'cd {SERVER_PATH} && nohup {python_cmd} run.py > server.log 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        print("  OK: Server started")
        print("Waiting 25 seconds...")
        time.sleep(25)
        
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
            print("\nChecking logs...")
            stdin, stdout, stderr = ssh.exec_command(f'tail -100 {SERVER_PATH}/server.log')
            print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    fix()

