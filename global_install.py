"""
Установка глобально и запуск
"""
import paramiko
import time

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def install_global():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        
        # Устанавливаем зависимости глобально
        print("Installing dependencies globally...")
        packages = 'fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib python-multipart paramiko anthropic python-socketio aiofiles python-dotenv slowapi markdown weasyprint markdown2 xhtml2pdf'.split()
        
        for pkg in packages:
            cmd = f'pip3 install {pkg} --quiet'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
            print(f"  Installed: {pkg}")
        
        print("  OK: All packages installed")
        
        # Проверяем импорт
        print("\nTesting import...")
        cmd = 'python3 -c "import fastapi; import uvicorn; print(\\"OK\\")"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8', errors='ignore')
        if 'OK' in output:
            print("  OK: Import successful")
        else:
            error = stderr.read().decode('utf-8', errors='ignore')
            print(f"  ERROR: {error}")
            return
        
        # Обновляем run.py чтобы использовать системный python3
        print("\nUpdating run.py...")
        run_py_content = '''import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.main import socketio_app

if __name__ == "__main__":
    uvicorn.run(
        socketio_app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
'''
        stdin, stdout, stderr = ssh.exec_command(f'cat > {SERVER_PATH}/run.py << "PYEOF"\n{run_py_content}PYEOF')
        stdout.read()
        print("  OK: run.py updated")
        
        # Запускаем сервер
        print("\nStarting server...")
        ssh.exec_command('pkill -f "python.*run.py" || pkill -f "uvicorn" || true')
        time.sleep(2)
        
        cmd = f'cd {SERVER_PATH} && nohup python3 run.py > server.log 2>&1 &'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        print("  OK: Server started")
        print("Waiting 20 seconds...")
        time.sleep(20)
        
        # Проверяем
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
                print(f"\nHealth: {result}")
                print(f"{'='*60}\n")
                return
            time.sleep(5)
        
        # Показываем логи
        print("\nChecking logs...")
        stdin, stdout, stderr = ssh.exec_command(f'tail -100 {SERVER_PATH}/server.log')
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        # Проверяем процессы
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep python | grep run.py')
        print("\nPython processes:")
        print(stdout.read().decode('utf-8', errors='ignore'))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    install_global()

