"""
Проверка pip и установка
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def check():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Проверяем pip
        print("Checking pip...")
        stdin, stdout, stderr = ssh.exec_command('which pip3 && pip3 --version')
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        # Устанавливаем pip если нужно
        print("\nInstalling/upgrading pip...")
        cmd = 'python3 -m ensurepip --upgrade || python3 -m pip install --upgrade pip'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        # Устанавливаем пакеты с выводом
        print("\nInstalling packages (this will take a few minutes)...")
        cmd = 'python3 -m pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" python-multipart paramiko anthropic python-socketio aiofiles python-dotenv slowapi markdown weasyprint markdown2 xhtml2pdf 2>&1 | tail -20'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        try:
            print(output)
        except:
            print("Installation output received")
        
        # Проверяем что установилось
        print("\nChecking installation...")
        cmd = 'python3 -m pip list | grep -E "(fastapi|uvicorn)"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8', errors='ignore')
        print(result)
        
        # Тестируем импорт
        print("\nTesting import...")
        cmd = 'python3 -c "import fastapi; import uvicorn; print(\\"OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        if 'OK' in output:
            print("  OK: Import successful!")
        else:
            print(f"  ERROR: {error}")
            return
        
        # Запускаем сервер
        print("\nStarting server...")
        ssh.exec_command('pkill -f "uvicorn" || pkill -f "python.*run" || true')
        time.sleep(2)
        
        cmd = f'cd {SERVER_PATH} && nohup python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > server.log 2>&1 &'
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
            print("\nServer logs:")
            stdin, stdout, stderr = ssh.exec_command(f'tail -100 {SERVER_PATH}/server.log')
            print(stdout.read().decode('utf-8', errors='ignore'))
            
            stdin, stdout, stderr = ssh.exec_command('netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp 2>/dev/null | grep 8000')
            print("\nPort 8000:")
            print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    check()

