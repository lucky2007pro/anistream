import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
import re

path = "/opt/anistream/core/settings.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("LOGIN_URL = 'auth_page'", "LOGIN_URL = 'login'")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Settings patched successfully.")
"""
    cmd = f'cat << "EOF" > /opt/anistream/patch_settings.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/patch_settings.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("PATCH OUT:", stdout.read().decode().strip())
    
    # Restart gunicorn
    ssh.exec_command("pkill -f 'gunicorn core.wsgi:application'")
    ssh.exec_command("cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &")
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
