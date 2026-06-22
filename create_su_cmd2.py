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
from dotenv import load_dotenv

load_dotenv('/opt/anistream/.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    user = User.objects.get(username="hojiakbar")
    user.set_password("admin")
    user.is_superuser = True
    user.is_staff = True
    user.is_admin_user = True
    user.save()
    print("Superuser updated")
except User.DoesNotExist:
    user = User.objects.create_superuser("hojiakbar", "hojiakbar@example.com", "admin")
    user.is_admin_user = True
    user.save()
    print("Superuser created")
"""
    cmd = f'cat << "EOF" > /opt/anistream/create_su2.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/create_su2.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
