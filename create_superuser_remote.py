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

from django.contrib.auth import get_user_model
User = get_user_model()

username = "hojiakbar"
password = "admin"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, "admin@example.com", password)
    print("Superuser yaratildi!")
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print("Superuser paroli yangilandi!")
"""
    cmd = f'cat << "EOF" > /opt/anistream/create_su.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/create_su.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
