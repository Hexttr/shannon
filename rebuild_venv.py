"""
Пересоздание venv и установка
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def rebuild():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Проверяем что есть
        stdin, stdout, stderr = ssh.exec_command(f'cd {SERVER_PATH} && ls -la')
        print("Directory contents:")
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        # Удаляем venv и создаем заново
        print("\nRecreating venv...")
        cmd = f'cd {SERVER_PATH} && rm -rf venv && python3 -m venv venv'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        # Проверяем что venv создан
        stdin, stdout, stderr = ssh.exec_command(f'cd {SERVER_PATH} && test -d venv && echo "EXISTS" || echo "NOT_EXISTS"')
        result = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"Venv exists: {result}")
        
        if 'NOT_EXISTS' in result:
            print("ERROR: Venv not created!")
            return
        
        # Устанавливаем зависимости используя прямой путь к pip
        print("\nInstalling dependencies...")
        cmd = f'cd {SERVER_PATH} && venv/bin/pip install --upgrade pip'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        cmd = f'cd {SERVER_PATH} && venv/bin/pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" python-multipart paramiko anthropic python-socketio aiofiles python-dotenv slowapi markdown weasyprint markdown2 xhtml2pdf'
        print("  Installing packages (this may take a few minutes)...")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Ждем завершения
        while True:
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("  OK: Packages installed")
        else:
            error = stderr.read().decode('utf-8', errors='ignore')
            print(f"  WARNING: {error[:300]}")
        
        # Проверяем установку
        cmd = f'cd {SERVER_PATH} && venv/bin/pip list | grep fastapi'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8', errors='ignore')
        if result:
            print(f"  Verified: {result.strip()}")
        
        # Тестируем импорт
        print("\nTesting import...")
        cmd = f'cd {SERVER_PATH} && venv/bin/python -c "import fastapi; import uvicorn; print(\\"OK\\")"'
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
        
        cmd = f'cd {SERVER_PATH} && nohup venv/bin/python run.py > server.log 2>&1 &'
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
            
            stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep 8000 || ss -tlnp | grep 8000')
            print("\nPort 8000 status:")
            print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    rebuild()

