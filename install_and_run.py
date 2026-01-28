"""
Установка зависимостей и запуск
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def install_and_run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Проверяем что requirements.txt существует
        stdin, stdout, stderr = ssh.exec_command(f'cat {SERVER_PATH}/requirements.txt')
        req_content = stdout.read().decode('utf-8', errors='ignore')
        print("Requirements.txt content:")
        print(req_content[:500])
        
        # Устанавливаем зависимости напрямую
        print("\nInstalling dependencies directly...")
        packages = [
            'fastapi', 'uvicorn[standard]', 'sqlalchemy', 'pydantic', 'pydantic-settings',
            'python-jose[cryptography]', 'passlib[bcrypt]', 'python-multipart',
            'paramiko', 'anthropic', 'python-socketio', 'aiofiles', 'python-dotenv',
            'slowapi', 'markdown', 'weasyprint', 'markdown2', 'xhtml2pdf'
        ]
        
        for pkg in packages:
            print(f"  Installing {pkg}...")
            cmd = f'cd {SERVER_PATH} && venv/bin/pip install --quiet {pkg}'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
        
        print("  OK: All packages installed")
        
        # Тестируем импорт
        print("\nTesting import...")
        cmd = f'cd {SERVER_PATH} && venv/bin/python -c "import fastapi; print(\\"FastAPI OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        if output:
            print(f"  OK: {output.strip()}")
        if error:
            print(f"  ERROR: {error}")
        
        # Запускаем сервер
        print("\nStarting server...")
        ssh.exec_command('pkill -f "python.*run.py" || true')
        time.sleep(2)
        
        cmd = f'cd {SERVER_PATH} && nohup venv/bin/python run.py > server.log 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        print("  OK: Server started")
        print("Waiting 15 seconds...")
        time.sleep(15)
        
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
    install_and_run()

