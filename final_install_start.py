"""
Финальная установка и запуск
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def install_and_start():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Устанавливаем typing-extensions отдельно
        print("Installing typing-extensions...")
        cmd = 'pip3 install --break-system-packages --ignore-installed typing-extensions'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        time.sleep(3)
        
        # Устанавливаем fastapi и остальные
        print("Installing fastapi, pydantic, anthropic...")
        cmd = 'pip3 install --break-system-packages fastapi pydantic pydantic-settings anthropic'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        time.sleep(5)
        
        # Проверяем импорт
        print("Testing import...")
        cmd = 'python3 -c "import fastapi; import uvicorn; print(\\"OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'OK' in output:
            print("  OK: Import successful!")
        else:
            error = stderr.read().decode('utf-8', errors='replace')
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
        print("Waiting 30 seconds...")
        time.sleep(30)
        
        # Проверяем
        for i in range(3):
            stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/health')
            result = stdout.read().decode('utf-8', errors='replace').strip()
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
        print("\nServer logs:")
        stdin, stdout, stderr = ssh.exec_command(f'tail -100 {SERVER_PATH}/server.log')
        print(stdout.read().decode('utf-8', errors='replace'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    install_and_start()

