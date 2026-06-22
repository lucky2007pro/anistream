import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
import os
with open('/opt/anistream/core/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "from django.urls import re_path" not in content and "re_path" not in content.split("\\n")[2]:
    content = content.replace("from django.urls import path", "from django.urls import path, re_path")
    with open('/opt/anistream/core/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("urls.py fixed!")
else:
    print("urls.py already has re_path.")
"""
    cmd = f'cat << "EOF" > /opt/anistream/fix_urls2.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/fix_urls2.py && pkill -f gunicorn && cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
