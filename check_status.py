"""
Проверка статуса сервера
"""
import paramiko

SSH_HOST = '72.56.79.153'
SSH_USER = 'root'
SSH_PASSWORD = 'm8J@2_6whwza6U'
SERVER_PATH = '/root/shannon/backend'

def check():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=10)
        
        # Проверяем health
        stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/health')
        result = stdout.read().decode('utf-8', errors='replace').strip()
        
        print('='*60)
        print('BACKEND STATUS')
        print('='*60)
        print(f'Health check result: {result}')
        
        if result:
            print('\nSUCCESS! Backend is running!')
            print(f'\nAPI URL: http://{SSH_HOST}:8000')
            print(f'Swagger Docs: http://{SSH_HOST}:8000/docs')
            print(f'ReDoc: http://{SSH_HOST}:8000/redoc')
        else:
            print('\nServer not responding. Checking logs...')
            stdin, stdout, stderr = ssh.exec_command(f'tail -30 {SERVER_PATH}/server.log')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            # Проверяем процессы
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep uvicorn | grep -v grep')
            print('\nPython processes:')
            print(stdout.read().decode('utf-8', errors='replace'))
        
        print('='*60)
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check()

