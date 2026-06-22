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
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
c = Client()
try:
    response = c.get('/chat/')
    print("STATUS:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
"""
    cmd = f'cat << "EOF" > /opt/anistream/test_chat_3.py\n{script}\nEOF\nexport DEBUG=True && /opt/anistream/venv/bin/python /opt/anistream/test_chat_3.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip()[:2000])
    print("ERR:", stderr.read().decode().strip()[:2000])
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
