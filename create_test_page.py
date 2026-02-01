#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

test_page = """<!DOCTYPE html>
<html>
<head>
    <title>API Test</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>API Test Page</h1>
    <button onclick="testLogin()">Test Login</button>
    <div id="result"></div>
    <script>
        async function testLogin() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Testing...';
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        username: 'admin',
                        password: 'admin'
                    })
                });
                
                const data = await response.json();
                resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                resultDiv.innerHTML = '<pre style="color: red;">Error: ' + error.message + '</pre>';
            }
        }
    </script>
</body>
</html>"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

sftp = ssh.open_sftp()
with sftp.file("/root/shannon/template/dist/test-api.html", 'w') as f:
    f.write(test_page)
sftp.close()

print("Тестовая страница создана: https://72.56.79.153/test-api.html")
print("Откройте её в браузере для тестирования API")

ssh.close()

