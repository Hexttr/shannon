"""
Проверка и запуск сервера с выводом ошибок
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
        
        # Проверяем структуру
        stdin, stdout, stderr = ssh.exec_command(f'cd {SERVER_PATH} && find app -name "*.py" | head -10')
        print("Python files:")
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        # Проверяем импорт
        print("\nTesting import...")
        cmd = f'cd {SERVER_PATH} && source venv/bin/activate && python -c "from app.main import socketio_app; print(\"Import OK\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
        
        # Запускаем сервер синхронно на 10 секунд чтобы увидеть ошибки
        print("\nStarting server (testing)...")
        cmd = f'cd {SERVER_PATH} && source venv/bin/activate && timeout 10 python run.py 2>&1 || true'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(12)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        print("Server output:")
        print(output)
        if error:
            print("Server errors:")
            print(error)
        
        # Проверяем логи
        print("\nServer log:")
        stdin, stdout, stderr = ssh.exec_command(f'cat {SERVER_PATH}/server.log 2>/dev/null || echo "No log file"')
        print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    check()

